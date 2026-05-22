# cc-switch

管理 `~/.claude/settings.json` 中的模型配置，支持多模型切换。

## 安装

```bash
pip install -e .
```

## 使用

```bash
cc-switch add              # 交互式添加模型
cc-switch list             # 列出所有已配置模型
cc-switch set <name>       # 切换到指定模型
cc-switch clear            # 清除模型配置
cc-switch remove <name>    # 删除指定模型
```

## 模型配置

模型配置存储在 `~/.cc-models.json`，每个模型包含三个字段：

| 字段 | 说明 |
|------|------|
| `ANTHROPIC_BASE_URL` | API 地址 |
| `ANTHROPIC_AUTH_TOKEN` | API Key，支持 `${ENV_VAR}` 引用环境变量 |
| `model` | 默认模型名称 |

`set claude` 等同于 `clear`，清除 settings.json 中的所有模型相关配置。