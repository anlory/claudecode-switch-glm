#!/usr/bin/env node

import { readFileSync, writeFileSync, mkdirSync } from "fs";
import { homedir } from "os";
import { join, dirname } from "path";
import { createInterface } from "readline";

const SETTINGS_PATH = join(homedir(), ".claude", "settings.json");
const MODELS_PATH = join(homedir(), ".cc-models.json");
const MODEL_ENV_KEYS = ["ANTHROPIC_BASE_URL", "ANTHROPIC_AUTH_TOKEN"];

// --- helpers ---

function load(path) {
  try {
    return JSON.parse(readFileSync(path, "utf-8"));
  } catch {
    return {};
  }
}

function save(path, data) {
  try {
    mkdirSync(dirname(path), { recursive: true });
  } catch {
    // directory already exists
  }
  writeFileSync(path, JSON.stringify(data, null, 2) + "\n", "utf-8");
}

function resolveToken(token) {
  const m = token.match(/^\$\{([A-Z_][A-Z0-9_]*)\}$/);
  return m ? process.env[m[1]] ?? "" : token;
}

function _ask(rl, prompt) {
  return new Promise((resolve) => {
    rl.question(prompt, (answer) => resolve(answer.trim()));
  });
}

// --- commands ---

async function cmdAdd() {
  const rl = createInterface({ input: process.stdin, output: process.stdout });
  const modelsData = load(MODELS_PATH);
  const models = modelsData.models ?? (modelsData.models = {});

  const name = await _ask(rl, "模型名称: ");
  if (!name) {
    console.error("错误: 模型名称不能为空");
    process.exit(1);
  }

  if (name in models) {
    const ans = await _ask(rl, `模型 "${name}" 已存在，是否覆盖? [y/N]: `);
    if (ans.toLowerCase() !== "y") {
      console.log("已取消");
      rl.close();
      return;
    }
  }

  const baseUrl = await _ask(rl, "ANTHROPIC_BASE_URL: ");
  if (!baseUrl) {
    console.error("错误: ANTHROPIC_BASE_URL 不能为空");
    process.exit(1);
  }

  const authToken = await _ask(rl, "ANTHROPIC_AUTH_TOKEN: ");
  if (!authToken) {
    console.error("错误: ANTHROPIC_AUTH_TOKEN 不能为空");
    process.exit(1);
  }

  if (/^\$\{[A-Z_][A-Z0-9_]*\}$/.test(authToken)) {
    const varName = authToken.slice(2, -1);
    if (!process.env[varName]) {
      console.warn(`警告: 环境变量 ${varName} 未设置`);
    }
  }

  const defaultModel = models[name]?.model ?? "opus";
  let model = await _ask(rl, `model [${defaultModel}]: `);
  if (!model) model = defaultModel;

  models[name] = {
    ANTHROPIC_BASE_URL: baseUrl,
    ANTHROPIC_AUTH_TOKEN: authToken,
    model,
  };
  save(MODELS_PATH, modelsData);
  console.log(`已添加模型 "${name}"`);
  rl.close();
}

function cmdList() {
  const modelsData = load(MODELS_PATH);
  const models = modelsData.models ?? {};

  if (Object.keys(models).length === 0) {
    console.log("暂无已配置的模型，使用 cc-switch add 添加");
    return;
  }

  const settings = load(SETTINGS_PATH);
  const currentEnv = settings.env ?? {};
  const currentModel = settings.model ?? "";

  let currentName = null;
  for (const [name, cfg] of Object.entries(models)) {
    if (
      currentEnv.ANTHROPIC_BASE_URL === cfg.ANTHROPIC_BASE_URL &&
      currentModel === cfg.model
    ) {
      currentName = name;
      break;
    }
  }
  if (!currentName && !currentEnv.ANTHROPIC_BASE_URL && !currentModel) {
    currentName = "claude";
  }

  console.log("可用模型:");
  for (const name of Object.keys(models)) {
    const marker = name === currentName ? " (当前使用)" : "";
    console.log(`  ${name}${marker}`);
  }
}

function cmdSet(name) {
  if (name === "claude") {
    cmdClear();
    return;
  }

  const modelsData = load(MODELS_PATH);
  const models = modelsData.models ?? {};

  if (!(name in models)) {
    console.error(`错误: 模型 "${name}" 不存在\n`);
    cmdList();
    process.exit(1);
  }

  const settings = load(SETTINGS_PATH);
  const cfg = models[name];
  if (!settings.env) settings.env = {};
  settings.env.ANTHROPIC_BASE_URL = cfg.ANTHROPIC_BASE_URL;
  settings.env.ANTHROPIC_AUTH_TOKEN = resolveToken(cfg.ANTHROPIC_AUTH_TOKEN);
  settings.model = cfg.model;
  save(SETTINGS_PATH, settings);
  console.log(`已切换到模型 "${name}"`);
}

function cmdRemove(name) {
  const modelsData = load(MODELS_PATH);
  const models = modelsData.models ?? {};

  if (!(name in models)) {
    console.error(`错误: 模型 "${name}" 不存在`);
    process.exit(1);
  }

  delete models[name];
  save(MODELS_PATH, modelsData);
  console.log(`已删除模型 "${name}"`);
}

function cmdClear() {
  const settings = load(SETTINGS_PATH);
  const env = settings.env ?? {};
  for (const key of MODEL_ENV_KEYS) delete env[key];
  delete settings.model;
  if (Object.keys(env).length === 0) delete settings.env;
  save(SETTINGS_PATH, settings);
  console.log("已清除模型配置");
}

function _usage() {
  console.log("用法: cc-switch <command> [name]\n");
  console.log("  cc-switch add          交互式添加模型");
  console.log("  cc-switch list         列出所有已配置模型");
  console.log("  cc-switch set <name>   切换到指定模型");
  console.log("  cc-switch remove <name> 删除指定模型");
  console.log("  cc-switch clear        清除模型配置");
}

function main() {
  const args = process.argv.slice(2);
  const command = args[0];
  const name = args[1];

  switch (command) {
    case "add":
      cmdAdd();
      break;
    case "list":
      cmdList();
      break;
    case "set":
      if (!name) _usage();
      else cmdSet(name);
      break;
    case "remove":
      if (!name) _usage();
      else cmdRemove(name);
      break;
    case "clear":
      cmdClear();
      break;
    default:
      _usage();
  }
}

main();