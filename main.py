"""cc_switch: 管理 ~/.claude/settings.json 中的模型配置，支持多模型切换"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

SETTINGS_PATH = Path.home() / ".claude" / "settings.json"
MODELS_PATH = Path.home() / ".cc-models.json"

MODEL_ENV_KEYS = {"ANTHROPIC_BASE_URL", "ANTHROPIC_AUTH_TOKEN"}


def load_settings() -> dict:
    if SETTINGS_PATH.exists():
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_settings(settings: dict) -> None:
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)
        f.write("\n")


def load_models() -> dict:
    if MODELS_PATH.exists():
        with open(MODELS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {}
    if "models" not in data:
        data["models"] = {}
    return data


def save_models(data: dict) -> None:
    MODELS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MODELS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def resolve_token(token: str) -> str:
    m = re.match(r"^\$\{([A-Z_][A-Z0-9_]*)\}$", token)
    if m:
        return os.environ.get(m.group(1), "")
    return token


def cmd_add() -> None:
    models_data = load_models()
    models = models_data["models"]

    name = input("模型名称: ").strip()
    if not name:
        print("错误: 模型名称不能为空")
        sys.exit(1)

    if name in models:
        ans = input(f'模型 "{name}" 已存在，是否覆盖? [y/N]: ').strip().lower()
        if ans != "y":
            print("已取消")
            return

    base_url = input("ANTHROPIC_BASE_URL: ").strip()
    if not base_url:
        print("错误: ANTHROPIC_BASE_URL 不能为空")
        sys.exit(1)

    auth_token = input("ANTHROPIC_AUTH_TOKEN: ").strip()
    if not auth_token:
        print("错误: ANTHROPIC_AUTH_TOKEN 不能为空")
        sys.exit(1)

    m = re.match(r"^\$\{([A-Z_][A-Z0-9_]*)\}$", auth_token)
    if m and not os.environ.get(m.group(1)):
        print(f"警告: 环境变量 {m.group(1)} 未设置")

    default_model = models.get(name, {}).get("model", "opus") if name in models else "opus"
    model = input(f"model [{default_model}]: ").strip()
    if not model:
        model = default_model

    models[name] = {
        "ANTHROPIC_BASE_URL": base_url,
        "ANTHROPIC_AUTH_TOKEN": auth_token,
        "model": model,
    }

    save_models(models_data)
    print(f'已添加模型 "{name}"')


def cmd_remove(name: str) -> None:
    models_data = load_models()
    models = models_data["models"]

    if name not in models:
        print(f'错误: 模型 "{name}" 不存在')
        sys.exit(1)

    del models[name]
    save_models(models_data)
    print(f'已删除模型 "{name}"')


def cmd_list() -> None:
    models_data = load_models()
    models = models_data["models"]

    if not models:
        print("暂无已配置的模型，使用 `cc-switch add` 添加")
        return

    settings = load_settings()
    current_env = settings.get("env", {})
    current_model = settings.get("model", "")

    current_name = None
    for name, cfg in models.items():
        if current_env.get("ANTHROPIC_BASE_URL") == cfg["ANTHROPIC_BASE_URL"] and current_model == cfg["model"]:
            current_name = name
            break

    if not current_name and not current_env.get("ANTHROPIC_BASE_URL") and not current_model:
        current_name = "claude"

    print("可用模型:")
    for name in models:
        marker = " (当前使用)" if name == current_name else ""
        print(f"  {name}{marker}")


def cmd_set(name: str) -> None:
    settings = load_settings()

    if name == "claude":
        cmd_clear()
        return

    models_data = load_models()
    models = models_data["models"]

    if name not in models:
        print(f'错误: 模型 "{name}" 不存在')
        print()
        cmd_list()
        sys.exit(1)

    cfg = models[name]

    if "env" not in settings:
        settings["env"] = {}

    settings["env"]["ANTHROPIC_BASE_URL"] = cfg["ANTHROPIC_BASE_URL"]
    settings["env"]["ANTHROPIC_AUTH_TOKEN"] = resolve_token(cfg["ANTHROPIC_AUTH_TOKEN"])
    settings["model"] = cfg["model"]

    save_settings(settings)
    print(f'已切换到模型 "{name}"')


def cmd_clear() -> None:
    settings = load_settings()
    env = settings.get("env", {})

    for key in MODEL_ENV_KEYS:
        env.pop(key, None)

    settings.pop("model", None)

    if not env:
        settings.pop("env", None)

    save_settings(settings)
    print("已清除模型配置")


def main():
    parser = argparse.ArgumentParser(
        prog="cc-switch",
        description="管理 ~/.claude/settings.json 中的模型配置，支持多模型切换",
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("add", help="交互式添加模型")
    subparsers.add_parser("list", help="列出所有已配置模型")
    remove_parser = subparsers.add_parser("remove", help="删除指定模型")
    remove_parser.add_argument("name", help="模型名称")
    set_parser = subparsers.add_parser("set", help="切换到指定模型")
    set_parser.add_argument("name", help="模型名称")
    subparsers.add_parser("clear", help="清除模型配置")

    args = parser.parse_args()

    if args.command == "add":
        cmd_add()
    elif args.command == "remove":
        cmd_remove(args.name)
    elif args.command == "list":
        cmd_list()
    elif args.command == "set":
        cmd_set(args.name)
    elif args.command == "clear":
        cmd_clear()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()