#!/usr/bin/env node
// Copies the skill directory into the locations Claude and Copilot read.

import { cp, mkdir, rm, readdir } from "node:fs/promises";
import { existsSync } from "node:fs";
import { spawnSync } from "node:child_process";
import { homedir } from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";

const NAME = "plain-style";
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const SOURCE = path.join(ROOT, ".claude", "skills", NAME);
const REQUIRED = ["SKILL.md", "references", "scripts"];
const MIN_PYTHON = [3, 9];
const SPEC = "github:blunttester/plain-style";

const USAGE = `Usage: npx ${SPEC} <install|uninstall|where> [options]

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
  reportPython(targets(args)[0], args.scope);
}

// Returns the first command that runs a new enough Python. If none does, returns
// the first older Python it found, or null.
function findPython() {
  // On Windows, "python3" is often a Store stub that prints a message and fails.
  const candidates = [["python3"], ["python"], ["py", "-3"]];
  let tooOld = null;
  for (const [cmd, ...pre] of candidates) {
    const result = spawnSync(
      cmd,
      [...pre, "-c", "import sys; print('%d.%d' % sys.version_info[:2])"],
      { encoding: "utf8" },
    );
    if (result.status !== 0 || !result.stdout) continue;
    const version = result.stdout.trim().split(".").map(Number);
    const found = { command: [cmd, ...pre].join(" "), version: version.join(".") };
    const ok =
      version[0] > MIN_PYTHON[0] ||
      (version[0] === MIN_PYTHON[0] && version[1] >= MIN_PYTHON[1]);
    if (ok) return { ...found, ok };
    tooOld ??= found;
  }
  return tooOld ? { ...tooOld, ok: false } : null;
}

// Every target holds the same copy, so the command names one of them.
function checkerCommand(python, target, scope) {
  const script = path.join(target, "scripts", "check_docs.py");
  // A global copy serves every project, so show the path that works from any of them.
  const shown = scope === "global" ? script : path.relative(process.cwd(), script);
  return `${python} ${shown.includes(" ") ? `"${shown}"` : shown} FILE.md`;
}

function reportPython(target, scope) {
  const need = MIN_PYTHON.join(".");
  const python = findPython();
  if (!python) {
    console.log(`\nwarning: no Python found. The checker needs Python ${need} or later.`);
    console.log(`The skill still installs, but the agent cannot run the checker.`);
    return;
  }
  if (!python.ok) {
    console.log(
      `\nwarning: ${python.command} is Python ${python.version}. The checker needs ${need} or later.`,
    );
    return;
  }
  console.log(`\nFound Python ${python.version}. Run the checker with:`);
  console.log(`  ${checkerCommand(python.command, target, scope)}`);
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
