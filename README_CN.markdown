# BSC Solidity 危险函数检测工具

[![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) [![Slither](https://img.shields.io/badge/Slither-0.9.7-green.svg)](https://github.com/crytic/slither)

一个轻量级 Python 脚本，用于快速审计 BSC (BNB Smart Chain) Solidity 智能合约的安全性。它扫描反编译或源代码，识别常见 rug pull 模式，如交易锁、无限授权和未放弃的 owner 权限。结合关键词匹配和 Slither 静态分析，生成 **DeepSeek 风格报告**，包含风险等级和实用建议。

> **为什么用这个工具？** 在 BSC meme 和代币的狂野世界中，一个快速的“红旗检测器”能帮你避开貔貅盘。完美用于 DYOR，在 10x 月球前先查查！

## 🚀 功能特点
- **关键词检测**：识别高风险函数（e.g., `selfdestruct`、模式切换），附带危害描述。
- **Slither 集成**：运行静态分析，检测重入、访问控制等漏洞。
- **报告输出**：结构化输出，带 🚨 风险徽章、代码片段和建议。
- **文件输入**：简单使用本地源代码文件（e.g., Heimdall-rs 反编译合约）。
- **Fallback 模式**：处理不可编译代码。

## 📦 安装
确保 Python 3.8+ 已安装。

### 依赖安装
```bash
pip install slither-analyzer==0.9.6 web3 requests
```

### Solidity 编译器（Slither 用）
```bash
pip install solc-select
solc-select install 0.8.0
solc-select use 0.8.0
```

## 🚀 快速开始
1. 创建文件夹（e.g., `bsc-audit`）。
2. 将脚本保存为 `bsc-auditor.py`。
3. 创建 `target.txt`，粘贴 Solidity 源代码（e.g., 反编译合约）。
4. 运行：
   ```bash
   python bsc-auditor.py
   ```

### 示例输出
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

## ⚠️ 局限性
- 针对反编译代码优化；在混淆合约上可能有假阳性。
- Slither 可能跳过不可编译代码（fallback 到关键词检测）。
- 完整审计需结合手动审查、RugDoc 或 TokenSniffer。

## 🤝 贡献
- Fork 仓库，创建分支（`git checkout -b feature/AmazingFeature`）。
- 提交变更（`git commit -m 'Add some AmazingFeature'`）。
- 推送分支（`git push origin feature/AmazingFeature`）。
- 开启 Pull Request！

## 📄 许可证
本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

---

**用 ❤️ 为 Web3 安全而建。DYOR 永远！**  
[GitHub 仓库](https://github.com/yourusername/bsc-auditor) | [问题反馈](https://github.com/yourusername/bsc-auditor/issues)