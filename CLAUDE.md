# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

`cc_glm` — 管理 `~/.claude/settings.json` 文件，将 Claude Code 切换到智谱 GLM 模型。单文件 CLI 工具（`main.py`），通过 `pyproject.toml` 注册为 `cc-glm` 命令。

## 开发命令

```bash
# 安装（开发模式）
pip install -e .

# 运行（安装后）
cc-glm on       # 开启 GLM 配置
cc-glm off      # 关闭 GLM 配置
cc-glm status   # 查看当前状态

# 代码检查
ruff check .
```

Python 版本：3.13，通过 `.python-version` 管理（`uv` 兼容）。