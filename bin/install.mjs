#!/usr/bin/env node
// Copies the skill directory into the locations Claude and Copilot read.

import { cp, mkdir, rm, readdir } from "node:fs/promises";
import { existsSync } from "node:fs";
import { homedir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const NAME = "plain-style";
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const SOURCE = path.join(ROOT, ".claude", "skills", NAME);
const REQUIRED = ["SKILL.md", "references", "scripts"];

const USAGE = `Usage: npx ${NAME} <install|uninstall|where> [options]

Options:
  --global          Install for every project, in your home directory
  --here            Install into the current repository (default)
  --agent <name>    claude, copilot, or all (default: all)
  --force           Overwrite an existing installation
  --dry-run         Print what would happen and change nothing
`;

function parseArgs(argv) {
  const args = { command: argv[0], scope: "here", agent: "all" };
  for (const arg of argv.slice(1)) {
    if (arg === "--global") args.scope = "global";
    else if (arg === "--here" || arg === "--local") args.scope = "here";
    else if (arg === "--force") args.force = true;
    else if (arg === "--dry-run") args.dryRun = true;
    else if (arg.startsWith("--agent=")) args.agent = arg.split("=")[1];
    else if (arg === "--agent") args.agentNext = true;
    else if (args.agentNext) {
      args.agent = arg;
      args.agentNext = false;
    } else {
      throw new Error(`unknown option: ${arg}`);
    }
  }
  if (!["claude", "copilot", "all"].includes(args.agent)) {
    throw new Error(`unknown agent: ${args.agent}`);
  }
  return args;
}

function targets({ scope, agent }) {
  const wanted = agent === "all" ? ["claude", "copilot"] : [agent];
  const paths = new Set();
  for (const one of wanted) {
    if (scope === "global") {
      // Claude reads ~/.claude/skills; Copilot reads ~/.agents/skills.
      const base = one === "claude" ? [".claude", "skills"] : [".agents", "skills"];
      paths.add(path.join(homedir(), ...base, NAME));
    } else {
      paths.add(path.join(process.cwd(), ".claude", "skills", NAME));
    }
  }
  return [...paths];
}

async function assertComplete() {
  if (!existsSync(SOURCE)) {
    throw new Error(`skill source is missing at ${SOURCE}`);
  }
  const found = new Set(await readdir(SOURCE));
  const missing = REQUIRED.filter((entry) => !found.has(entry));
  if (missing.length) {
    // scripts/ without references/ means every banned-word rule silently vanishes.
    throw new Error(`skill source is incomplete, missing: ${missing.join(", ")}`);
  }
}

async function install(args) {
  await assertComplete();
  for (const target of targets(args)) {
    if (existsSync(target) && !args.force) {
      console.log(`exists, skipped: ${target}  (use --force to overwrite)`);
      continue;
    }
    if (args.dryRun) {
      console.log(`would install: ${target}`);
      continue;
    }
    await mkdir(path.dirname(target), { recursive: true });
    await rm(target, { recursive: true, force: true });
    await cp(SOURCE, target, {
      recursive: true,
      filter: (src) => !src.includes("__pycache__"),
    });
    console.log(`installed: ${target}`);
  }
  console.log(`\nThe checker needs Python 3.11 or later. Run it with:`);
  console.log(`  python3 <skill>/scripts/check_docs.py FILE.md`);
}

async function uninstall(args) {
  for (const target of targets(args)) {
    if (!existsSync(target)) {
      console.log(`not present: ${target}`);
      continue;
    }
    if (args.dryRun) {
      console.log(`would remove: ${target}`);
      continue;
    }
    await rm(target, { recursive: true, force: true });
    console.log(`removed: ${target}`);
  }
}

function where(args) {
  for (const target of targets(args)) {
    console.log(`${existsSync(target) ? "present" : "absent "}  ${target}`);
  }
}

async function main() {
  let args;
  try {
    args = parseArgs(process.argv.slice(2));
  } catch (error) {
    console.error(`${error.message}\n\n${USAGE}`);
    process.exit(2);
  }

  try {
    if (args.command === "install") await install(args);
    else if (args.command === "uninstall") await uninstall(args);
    else if (args.command === "where") where(args);
    else {
      console.error(USAGE);
      process.exit(2);
    }
  } catch (error) {
    console.error(`error: ${error.message}`);
    process.exit(1);
  }
}

main();
