# cc_glm

管理 `~/.claude/settings.json` 中的 GLM 环境变量配置，用于将 Claude Code 切换到智谱 GLM 模型。

## 安装

```bash
pip install -e .
```

## 配置

设置系统环境变量 `GLM_API_KEY` 为你的 API Key：

```bash
export GLM_API_KEY=your_api_key_here
```

## 使用

```bash
cc-glm on      # 开启 GLM 模型配置（模型设为 opus）
cc-glm off     # 关闭 GLM 模型配置（移除模型设置）
cc-glm status  # 检查当前配置状态
```

## 管理的环境变量

| 变量 | 值 |
|------|-----|
| `ANTHROPIC_AUTH_TOKEN` | 从环境变量 `GLM_API_KEY` 读取 |
| `ANTHROPIC_BASE_URL` | `https://open.bigmodel.cn/api/anthropic` |
| `API_TIMEOUT_MS` | `3000000` |
| `ANTHROPIC_DEFAULT_HAIKU_MODEL` | `glm-4.5-air` |
| `ANTHROPIC_DEFAULT_SONNET_MODEL` | `glm-5-turbo` |
| `ANTHROPIC_DEFAULT_OPUS_MODEL` | `glm-5.1` |
| `CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC` | `1` |
| `model` | `opus`（on 时设置，off 时移除） |
