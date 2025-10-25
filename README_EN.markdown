# BSC Solidity Dangerous Function Auditor

[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Slither](https://img.shields.io/badge/Slither-0.9.7-green.svg)](https://github.com/crytic/slither)

A lightweight Python script for quick security audits of BSC (BNB Smart Chain) Solidity smart contracts. It scans decompiled or source code to identify common rug pull indicators like trading locks, unlimited approvals, and unrenounced ownership. Combines keyword matching with Slither static analysis to generate **DeepSeek-style reports** with risk levels and actionable advice.

> **Why this tool?** In the wild world of BSC memes and tokens, a fast "red flag detector" can save you from Pixiu scams. Perfect for DYOR before that 10x moonshot!

## 🚀 Features
- **Keyword Detection**: Spots high-risk patterns (e.g., `selfdestruct`, mode switches) with harm descriptions.
- **Slither Integration**: Static analysis for reentrancy, access control, and more.
- **Report Output**: Structured output with 🚨 risk badges, code snippets, and suggestions.
- **File Input**: Simple local files (e.g., decompiled contracts from Heimdall-rs).
- **Fallback Mode**: Handles non-compilable code gracefully.

## 📦 Installation
Ensure Python 3.8+ is installed.

### Dependencies
```bash
pip install slither-analyzer==0.9.6 web3 requests
```

### Solidity Compiler (for Slither)
```bash
pip install solc-select
solc-select install 0.8.0
solc-select use 0.8.0
```

## 🚀 Quick Start
1. Create a folder (e.g., `bsc-audit`).
2. Save the script as `bsc-auditor.py`.
3. Create `target.txt` and paste the Solidity source code (e.g., decompiled contract).
4. Run:
   ```bash
   python bsc-auditor.py
   ```

### Example Output
```
## 🚨 BSC 合约危险函数审计报告

### 🔍 检测到危险函数 (1 个)
#### MODE_SWITCH (中 风险)
**匹配次数**: 11
**代码片段**:
require(unresolved_c5c03af3 - 0x01, "Token: Transfer is restricted");
**潜在危害**: Trading Lock: Owner can disable transfers (e.g., set to restricted mode), trapping user funds (Pixiu scam).

### ⚠️ 风险结论
- **风险等级**: 高风险 🔴（检测到 1 个危险函数）
- **建议**: 结合链上数据 DYOR，检查 owner 活动。

### 📊 Slither 静态分析结果
- access-control: Owner can call setMode to lock transfers.
```

## ⚠️ Limitations
- Optimized for decompiled code; may have false positives on obfuscated contracts.
- Slither may skip non-compilable code (relies on keyword detection).
- For full audits, pair with manual review, RugDoc, or TokenSniffer.

## 🤝 Contributing
- Fork the repo and create a branch (`git checkout -b feature/AmazingFeature`).
- Commit changes (`git commit -m 'Add some AmazingFeature'`).
- Push to branch (`git push origin feature/AmazingFeature`).
- Open a Pull Request!

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Built with ❤️ for Web3 safety. DYOR always!**  
[GitHub Repo](https://github.com/yourusername/bsc-auditor) | [Issues](https://github.com/yourusername/bsc-auditor/issues)