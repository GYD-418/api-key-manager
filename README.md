# 🤖 大模型API密钥管理器

一个基于PyQt5开发的API密钥管理工具，支持多种大模型API的统一管理、测试和调用。

## ✨ 功能特点

- 🔐 **密钥管理**：添加、编辑、删除API密钥
- ✅ **密钥验证**：批量验证API密钥有效性，显示响应时间
- 💬 **对话测试**：直接测试API连接
- 🌈 **多API支持**：支持通义千问、DeepSeek、Moonshot、智谱AI、MiniMax等多种API
- 🎨 **深色主题**：护眼深色UI设计

## 📦 安装

```bash
# 安装依赖
pip install -r requirements.txt
```

## 🚀 运行

```bash
python app_pyqt.py
```

## 📱 打包

```bash
python build.py
```

打包后的可执行文件在 `dist/APIKeyManager.exe`

## 🛠️ 技术栈

- Python 3.x
- PyQt5
- requests

## 📄 许可证

MIT