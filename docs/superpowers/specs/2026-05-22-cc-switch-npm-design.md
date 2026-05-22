# cc-switch npm 版设计

日期: 2026-05-22

## 目标

将 Python 版 `cc-switch` 用纯 Node.js 重写为 npm 包，与 Python 版共享数据和行为，用户可根据偏好选择安装方式。

## 文件结构

```
npm/
├── package.json
├── index.js          # 单文件实现，~200 行
└── README.md
```

## 技术选型

- 零外部依赖，仅使用 Node.js 内置模块：`fs`、`path`、`os`、`readline`
- `package.json` 中 `"bin": { "cc-switch": "./index.js" }`，通过 shebang 指定 node
- 最低 Node.js 版本：18（LTS），使用 ESM（`import` 语法）

## 命令

| 命令 | 行为 |
|------|------|
| `cc-switch add` | 交互式添加模型，readline 逐行输入 name/url/token/model |
| `cc-switch list` | 列出所有模型，标注当前使用的 |
| `cc-switch set <name>` | 切换到指定模型，写入 settings.json |
| `cc-switch remove <name>` | 删除指定模型 |
| `cc-switch clear` | 清除 settings.json 中的模型配置 |

`set claude` 等同于 `clear`。

## 数据流

- 读取 `~/.claude/settings.json`（读写）
- 读取 `~/.cc-models.json`（读写）
- 两个文件的格式和路径与 Python 版完全一致
- 环境变量引用 `${VAR_NAME}` 通过 `process.env` 解析

## 包发布

- 发布到 npm registry，包名 `cc-switch`
- 用户通过 `npm install -g cc-switch` 安装