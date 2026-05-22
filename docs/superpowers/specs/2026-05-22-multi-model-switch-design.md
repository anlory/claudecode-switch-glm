# 多模型切换 CLI 设计

## 概述

将 `cc_glm` 从只支持 GLM 的单模型切换工具，改造为支持任意模型的通用切换工具。所有模型通过 `~/.cc-models.json` 文件管理，CLI 提供增删查切功能。

## 命令

```
cc-glm add              # 交互式添加模型
cc-glm remove <name>    # 删除指定模型
cc-glm list             # 列出所有已配置模型
cc-glm set <name>       # 切换到指定模型
cc-glm clear            # 清除 settings.json 中的模型配置
```

## 数据模型

### `~/.cc-models.json` — 用户模型配置

```json
{
  "models": {
    "deepseek": {
      "ANTHROPIC_BASE_URL": "https://api.deepseek.com/anthropic",
      "ANTHROPIC_AUTH_TOKEN": "${DEEPSEEK_API_KEY}",
      "model": "opus"
    },
    "glm": {
      "ANTHROPIC_BASE_URL": "https://open.bigmodel.cn/api/anthropic",
      "ANTHROPIC_AUTH_TOKEN": "${GLM_API_KEY}",
      "model": "opus"
    }
  }
}
```

- 每个模型三个字段：`ANTHROPIC_BASE_URL`、`ANTHROPIC_AUTH_TOKEN`、`model`
- `ANTHROPIC_AUTH_TOKEN` 支持 `${ENV_VAR}` 语法，set 时从系统环境变量读取
- 文件初始为空或不存在，用户自行添加

### `~/.claude/settings.json` — 目标写入

`set <name>` 时合并写入 `env` 和 `model` 字段，不删除已有的其他 env vars。写入内容：

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://api.deepseek.com/anthropic",
    "ANTHROPIC_AUTH_TOKEN": "<从环境变量解析后的实际值>"
  },
  "model": "opus"
}
```

## 命令行为

### `add`

交互式输入四个字段，名称冲突时询问是否覆盖：

```
模型名称: deepseek
ANTHROPIC_BASE_URL: https://api.deepseek.com/anthropic
ANTHROPIC_AUTH_TOKEN: ${DEEPSEEK_API_KEY}
model [opus]: opus
已添加模型 "deepseek"
```

- `ANTHROPIC_AUTH_TOKEN` 用 `${VAR}` 引用环境变量时，检查变量是否存在，不存在则警告但允保存
- `model` 有默认值 `opus`

### `remove <name>`

- 直接从 `~/.cc-models.json` 中删除对应条目
- 不存在的模型报错

### `list`

- 列出 `~/.cc-models.json` 中所有模型
- 读取 `~/.claude/settings.json` 中当前 env vars，匹配判断当前使用的是哪个模型
- 标注当前激活的模型

### `set <name>`

- 从 `~/.cc-models.json` 读取模型配置
- `${ENV_VAR}` 解析为实际的环境变量值
- 合并写入 `settings.json` 的 `env`（不删除已有的其他 key）
- 写入 `model` 字段
- `claude` 是特殊名称：即使不在配置文件中，`set claude` 也能执行，效果等同于 `clear`
- 不存在的模型报错

### `clear`

- 从 `settings.json` 中删除 `ANTHROPIC_BASE_URL`、`ANTHROPIC_AUTH_TOKEN` 和 `model` 字段
- 保留其他 env vars 不变

## 错误处理

| 场景 | 行为 |
|------|------|
| `set` 不存在的模型（非 claude） | 报错 + 提示可用模型列表 |
| `add` 名冲突 | 询问是否覆盖 |
| `add` 引用的环境变量不存在 | 警告但允许保存 |
| `remove` 不存在的模型 | 报错 |
| `~/.cc-models.json` 不存在 | 自动创建空文件 |

## 实现

单文件 `main.py`，改动范围：

1. 移除 `cmd_on`、`cmd_off`、`cmd_status` 和 GLM 相关常量
2. 新增 `MODELS_PATH = Path.home() / ".cc-models.json"`
3. 新增 `load_models()` / `save_models()` 函数
4. 新增 `resolve_token()` 处理 `${ENV_VAR}` 语法
5. 新增 `cmd_add`、`cmd_remove`、`cmd_list`、`cmd_set`、`cmd_clear`
6. 更新 `pyproject.toml` 中的 description
7. 更新 `README.md`

保持 `SETTINGS_PATH`、`load_settings()`、`save_settings()` 不变。