import re
import os
import tempfile
from web3 import Web3  # 链上验证
from slither.slither import Slither
import logging
import sys
from typing import List, Dict
import requests  # DexScreener API

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 危险函数/模式（加排除条件）
DANGER_PATTERNS = {
    'selfdestruct': {
        'pattern': r'selfdestruct\s*\(\s*payable\s*\(\s*[^)]+\)\s*\)',
        'string_match': r'selfdestruct',
        'exclude': r'renounced|safe|emergency',  # 排除安全上下文
        'level': '高',
        'harm': 'Rug Pull: Owner can destroy contract and drain funds.'
    },
    'unlimited_approve': {
        'pattern': r'approve\s*\(\s*[^,]+,\s*type\s*\(\s*uint256\s*\)\.max\s*\)',
        'string_match': r'uint256\.max',
        'exclude': r'safe|trusted|whitelist',  # 排除白名单场景
        'level': '高',
        'harm': 'Unlimited Approval: Infinite spending risk.'
    },
    'owner_mint': {
        'pattern': r'_mint\s*\(\s*msg\.sender\s*,\s*[^)]+\)\s*',
        'string_match': r'_mint\s*\(\s*msg\.sender',
        'exclude': r'fixed|initial|team',  # 排除初始 mint
        'level': '高',
        'harm': 'Unlimited Mint: Supply dilution attack.'
    },
    'mode_switch': {
        'pattern': r'setMode|tradingEnabled|transferRestricted\s*\(\s*[^)]+\)\s*',
        'string_match': r'Transfer is restricted|Invalid transfer|unresolved_c5c03af3',
        'exclude': r'renounced|decentralized|community',  # 排除去中心化模式
        'level': '中',
        'harm': 'Trading Lock: Owner can disable transfers, trapping funds.'
    },
    'no_renounce': {
        'pattern': r'renounceOwnership\s*\{\s*\}\s*',
        'string_match': r'renounceOwnership',
        'exclude': None,  # 无排除，始终中风险
        'level': '中',
        'harm': 'Owner Retention: Full control retained.'
    }
}

class BSCContractAuditor:
    def __init__(self, source_file: str, ca: str = None):
        """从文件读取源码，可选 CA 链上查"""
        if not os.path.exists(source_file):
            print(f"错误: 未找到 {source_file} 文件。请创建 {source_file} 并粘贴合约源代码。")
            sys.exit(1)
        with open(source_file, 'r', encoding='utf-8') as f:
            self.source = f.read()
        self.source = self._clean_source(self.source)
        self.dangers = self._detect_dangers()
        self.slither_issues = self._run_slither()
        self.onchain_risk = self._check_onchain_risk(ca) if ca else {}

    def _clean_source(self, source: str) -> str:
        """清理源码：移除 License、注释、var_ 混淆行"""
        lines = source.split('\n')
        cleaned = []
        in_license = False
        for line in lines:
            line = line.strip()
            if 'MIT License' in line or 'Copyright' in line or 'Permission is hereby granted' in line:
                in_license = True
                continue
            if in_license and line == '':
                in_license = False
                continue
            # 跳过注释和 var_ 混淆行
            if line.startswith('//') or line.startswith('/*') or line.startswith('*/') or re.match(r'var_[a-z]', line):
                continue
            # 保留核心 Solidity
            if line.startswith('pragma') or line.startswith('contract') or line.startswith('function') or line.startswith('mapping') or line.startswith('event') or line.startswith('require') or line.startswith('emit') or line.startswith('storage_map'):
                cleaned.append(line)
        return '\n'.join(cleaned)

    def _detect_dangers(self) -> List[Dict]:
        """自定义关键词检测危险函数（加排除逻辑）"""
        dangers = []
        for name, info in DANGER_PATTERNS.items():
            # 正则匹配
            matches = re.findall(info['pattern'], self.source, re.IGNORECASE | re.MULTILINE)
            # 字符串匹配
            string_matches = re.findall(info['string_match'], self.source, re.IGNORECASE | re.MULTILINE)
            total_matches = len(matches) + len(string_matches)
            if total_matches > 0:
                # 检查排除条件
                if info.get('exclude'):
                    exclude_matches = re.findall(info['exclude'], self.source, re.IGNORECASE | re.MULTILINE)
                    if len(exclude_matches) > 0:
                        logging.info(f"{name} 匹配但有排除词 ({len(exclude_matches)} 次)，标记为低风险。")
                        continue  # 排除假阳性
                snippet = self._extract_snippet(info['string_match']) if string_matches else self._extract_snippet(info['pattern'])
                dangers.append({
                    'function': name,
                    'matches': total_matches,
                    'level': info['level'],
                    'code_snippet': snippet,
                    'harm': info['harm']
                })
        return dangers

    def _extract_snippet(self, pattern: str) -> str:
        """提取匹配代码片段（扩展上下文）"""
        match = re.search(pattern, self.source, re.IGNORECASE | re.MULTILINE)
        if match:
            lines = self.source.split('\n')
            start = max(0, match.span()[0] // 100 - 5)
            end = min(len(lines), start + 10)
            snippet_lines = [line for line in lines[start:end] if line.strip() and not re.match(r'var_[a-z]', line.strip())]
            snippet = '\n'.join(snippet_lines)
            return snippet[:300] + '...' if len(snippet) > 300 else snippet
        return "No snippet found"

    def _run_slither(self) -> List[str]:
        """运行 Slither 静态分析（fallback）"""
        temp_sol = None
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.sol', delete=False, encoding='utf-8') as f:
                f.write(self.source)
                temp_sol = f.name
            slither = Slither(temp_sol)
            slither.run_detectors()
            issues = []
            for detector in slither.detectors:
                results = detector.detect()
                for result in results:
                    issues.append(f"{detector.NAME}: {result.description}")
            return issues
        except Exception as e:
            logging.warning(f"Slither 编译失败 (反编译代码常见): {str(e)}。依赖自定义检测。")
            return ["Slither skipped: Decompiled code not compilable. Use custom detection for risks."]
        finally:
            if temp_sol and os.path.exists(temp_sol):
                os.unlink(temp_sol)

    def _check_onchain_risk(self, ca: str) -> Dict:
        """链上风险查（owner renounce、市值）"""
        w3 = Web3(Web3.HTTPProvider('https://bsc-dataseed.binance.org/'))
        ca = w3.to_checksum_address(ca)
        try:
            # 查 owner (假设 ABI)
            abi = [{"type":"function","name":"owner","inputs":[],"outputs":[{"type":"address"}]}]
            contract = w3.eth.contract(address=ca, abi=abi)
            owner = contract.functions.owner().call()
            renounced = owner == '0x0000000000000000000000000000000000000000'
            # 查市值 (DexScreener API)
            dex_url = f"https://api.dexscreener.com/latest/dex/tokens/{ca}"
            response = requests.get(dex_url)
            market_cap = response.json().get('pairs', [{}])[0].get('marketCap', 'N/A') if response.ok else 'N/A'
            return {'owner_renounced': renounced, 'market_cap': market_cap}
        except Exception as e:
            return {'error': str(e)}

    def generate_report(self) -> str:
        """生成 DeepSeek 风格报告"""
        report = "## 🚨 BSC 合约危险函数审计报告\n\n"
        num_dangers = len(self.dangers)
        if num_dangers > 0:
            report += f"### 🔍 检测到危险函数 ({num_dangers} 个)\n"
            for danger in self.dangers:
                report += f"#### {danger['function'].upper()} ({danger['level']} 风险)\n"
                report += f"**匹配次数**: {danger['matches']}\n"
                report += f"**代码片段**:\n```solidity\n{danger['code_snippet']}\n```\n"
                report += f"**潜在危害**: {danger['harm']}\n\n"
            report += f"### ⚠️ 风险结论\n- **风险等级**: 高风险 {chr(127988 if num_dangers > 2 else 127988 if num_dangers > 0 else 128309)}（检测到 {num_dangers} 个危险函数）\n- **建议**: 结合链上数据 DYOR，检查 owner 活动。\n\n"
        else:
            report += "### 🟢 无危险函数检测\n- 基本 ERC-20 合规，但需进一步 Slither 分析。\n\n"

        report += "### 📊 Slither 静态分析结果\n"
        for issue in self.slither_issues:
            report += f"- {issue}\n"

        return report

def main():
    print("BSC Solidity 危险函数检测工具 (文件版)")
    
    auditor = BSCContractAuditor('target.txt')
    report = auditor.generate_report()
    print(report)

if __name__ == "__main__":
    main()