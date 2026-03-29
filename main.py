"""cc_glm: 管理 ~/.claude/settings.json 中的 GLM 环境变量配置"""

import argparse
import json
import os
import sys
from pathlib import Path

SETTINGS_PATH = Path.home() / ".claude" / "settings.json"

ANTHROPIC_BASE_URL = "https://open.bigmodel.cn/api/anthropic"
API_TIMEOUT_MS = "3000000"
ANTHROPIC_DEFAULT_HAIKU_MODEL = "glm-4.5-air"
ANTHROPIC_DEFAULT_SONNET_MODEL = "glm-5-turbo"
ANTHROPIC_DEFAULT_OPUS_MODEL = "glm-5.1"
CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC = "1"
GLM_DEFAULT_MODEL = "opus"

# GLM 相关的环境变量（token 从系统环境变量 GLM_API_KEY 读取，其余使用上面定义的常量）
GLM_ENV_VARS = {
    "ANTHROPIC_AUTH_TOKEN": os.environ.get("GLM_API_KEY", ""),
    "ANTHROPIC_BASE_URL": ANTHROPIC_BASE_URL,
    "API_TIMEOUT_MS": API_TIMEOUT_MS,
    "ANTHROPIC_DEFAULT_HAIKU_MODEL": ANTHROPIC_DEFAULT_HAIKU_MODEL,
    "ANTHROPIC_DEFAULT_SONNET_MODEL": ANTHROPIC_DEFAULT_SONNET_MODEL,
    "ANTHROPIC_DEFAULT_OPUS_MODEL": ANTHROPIC_DEFAULT_OPUS_MODEL,
    "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC,
}


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


def cmd_status() -> None:
    """检查当前配置状态"""
    settings = load_settings()
    env = settings.get("env", {})

    print(f"配置文件: {SETTINGS_PATH}")
    print()

    configured = []
    missing = []
    for key, expected_value in GLM_ENV_VARS.items():
        actual_value = env.get(key)
        if actual_value is None:
            missing.append(key)
        elif actual_value == expected_value:
            configured.append(key)
        else:
            configured.append(key)
            print(f"  [已修改] {key}")
            print(f"           期望: {expected_value}")
            print(f"           实际: {actual_value}")

    if configured and not any(v != env.get(k) for k, v in GLM_ENV_VARS.items() if k in env):
        print("  [已配置] " + "\n  [已配置] ".join(
            k for k in GLM_ENV_VARS if k in env and env[k] == GLM_ENV_VARS[k]
        ))

    if missing:
        print()
        print("  [缺失] " + "\n  [缺失] ".join(missing))

    print()
    all_match = all(env.get(k) == v for k, v in GLM_ENV_VARS.items())
    if all_match:
        print("状态: 所有 GLM 环境变量已正确配置")
    elif env:
        print("状态: 部分变量已配置（可能已被修改）")
    else:
        print("状态: 未配置任何 GLM 环境变量")


def cmd_on() -> None:
    """开启 GLM 环境变量"""
    if not os.environ.get("GLM_API_KEY"):
        print("错误: 未配置环境变量 GLM_API_KEY，请先设置后再开启")
        sys.exit(1)

    settings = load_settings()
    if "env" not in settings:
        settings["env"] = {}

    for key, value in GLM_ENV_VARS.items():
        settings["env"][key] = value

    settings["model"] = GLM_DEFAULT_MODEL

    save_settings(settings)
    print("已开启 GLM 模型配置")


def cmd_off() -> None:
    """关闭 GLM 环境变量"""
    settings = load_settings()
    env = settings.get("env", {})

    removed = []
    for key in GLM_ENV_VARS:
        if key in env:
            del env[key]
            removed.append(key)

    if settings.pop("model", None) is not None:
        removed.append("model")

    if not env:
        settings.pop("env", None)

    save_settings(settings)

    if removed:
        print("已关闭 GLM 模型配置")
    else:
        print("GLM 环境变量未配置，无需关闭")


def main():
    parser = argparse.ArgumentParser(
        prog="cc-glm",
        description="管理 ~/.claude/settings.json 中的 GLM 环境变量配置",
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("on", help="开启 GLM 模型配置")
    subparsers.add_parser("off", help="关闭 GLM 模型配置")
    subparsers.add_parser("status", help="检查 GLM 环境变量配置状态")

    args = parser.parse_args()

    if args.command == "on":
        cmd_on()
    elif args.command == "off":
        cmd_off()
    elif args.command == "status":
        cmd_status()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
