#!/usr/bin/env node

/**
 * cliskill cross-platform installer
 *
 * Usage:
 *   npx cliskill                  # Install cliskill + dependencies
 *   npx cliskill --dry-run        # Preview without changes
 *   npx cliskill --uninstall      # Remove cliskill
 *
 * Works on macOS, Linux, and Windows (PowerShell or cmd).
 * Auto-detects installed AI coding tools and installs to all of them.
 * Auto-installs dependencies (/clarity, /agent-skill-creator) by default.
 */

import { execSync, execFileSync } from "node:child_process";
import { existsSync, mkdirSync, rmSync, symlinkSync, readlinkSync, lstatSync, cpSync } from "node:fs";
import { join, resolve, dirname } from "node:path";
import { homedir, platform as osPlatform } from "node:os";

// --- Config ---

const REPO_URL = "https://github.com/FrancyJGLisboa/cliskill.git";
const DEPS = {
  clarity: "https://github.com/FrancyJGLisboa/clarity.git",
  "agent-skill-creator": "https://github.com/FrancyJGLisboa/agent-skill-creator.git",
};

const IS_WIN = osPlatform() === "win32";
const HOME = homedir();

// --- CLI args ---

const args = process.argv.slice(2);
const DRY_RUN = args.includes("--dry-run");
const UNINSTALL = args.includes("--uninstall");
const HELP = args.includes("--help") || args.includes("-h");

if (HELP) {
  console.log(`
cliskill installer — AI-agent-friendly CLI skill framework

Usage:
  npx cliskill               Install cliskill + all dependencies
  npx cliskill --dry-run     Preview what would be installed
  npx cliskill --uninstall   Remove cliskill from all platforms

Requirements:
  - git (to clone skill repositories)
  - Python 3.10+ (to run skills at runtime)

What gets installed:
  1. /cliskill        — the pipeline orchestrator
  2. /clarity         — specification engine (auto-installed)
  3. /agent-skill-creator — implementation engine (auto-installed)
`);
  process.exit(0);
}

// --- Logging ---

const GREEN = "\x1b[32m";
const YELLOW = "\x1b[33m";
const RED = "\x1b[31m";
const CYAN = "\x1b[36m";
const BOLD = "\x1b[1m";
const RESET = "\x1b[0m";

function ok(msg) { console.log(`  ${GREEN}✓${RESET} ${msg}`); }
function warn(msg) { console.log(`  ${YELLOW}⚠${RESET} ${msg}`); }
function fail(msg) { console.log(`  ${RED}✗${RESET} ${msg}`); }
function info(msg) { console.log(`  ${CYAN}→${RESET} ${msg}`); }
function header(msg) { console.log(`\n${BOLD}${msg}${RESET}`); }

// --- Prerequisite checks ---

function which(cmd) {
  try {
    const out = IS_WIN
      ? execSync(`where ${cmd}`, { stdio: ["pipe", "pipe", "pipe"] }).toString().trim()
      : execSync(`command -v ${cmd}`, { stdio: ["pipe", "pipe", "pipe"] }).toString().trim();
    return out.split(/\r?\n/)[0] || null;
  } catch {
    return null;
  }
}

function checkPrereqs() {
  header("Checking prerequisites");
  let allOk = true;

  // git
  const gitPath = which("git");
  if (gitPath) {
    try {
      const ver = execSync("git --version", { stdio: ["pipe", "pipe", "pipe"] }).toString().trim();
      ok(`git: ${ver}`);
    } catch {
      ok(`git: ${gitPath}`);
    }
  } else {
    fail("git is not installed");
    console.log(`\n    Install git:`);
    if (IS_WIN) {
      console.log(`      https://git-scm.com/download/win`);
      console.log(`      or: winget install Git.Git`);
    } else if (osPlatform() === "darwin") {
      console.log(`      xcode-select --install`);
      console.log(`      or: brew install git`);
    } else {
      console.log(`      sudo apt install git   (Debian/Ubuntu)`);
      console.log(`      sudo dnf install git   (Fedora/RHEL)`);
    }
    allOk = false;
  }

  // python
  const py3 = which("python3");
  const py = which("python");
  const pythonCmd = py3 || py;

  if (pythonCmd) {
    try {
      const ver = execSync(`${pythonCmd} --version`, { stdio: ["pipe", "pipe", "pipe"] }).toString().trim();
      const match = ver.match(/(\d+)\.(\d+)/);
      if (match && (parseInt(match[1]) < 3 || (parseInt(match[1]) === 3 && parseInt(match[2]) < 10))) {
        fail(`${ver} — Python 3.10+ required`);
        allOk = false;
      } else {
        ok(`${ver} (${pythonCmd})`);
      }
    } catch {
      ok(`python: ${pythonCmd}`);
    }
  } else {
    fail("Python is not installed");
    console.log(`\n    Install Python 3.10+:`);
    if (IS_WIN) {
      console.log(`      https://python.org/downloads`);
      console.log(`      or: winget install Python.Python.3.12`);
    } else if (osPlatform() === "darwin") {
      console.log(`      brew install python`);
    } else {
      console.log(`      sudo apt install python3   (Debian/Ubuntu)`);
      console.log(`      sudo dnf install python3   (Fedora/RHEL)`);
    }
    allOk = false;
  }

  return allOk;
}

// --- Platform detection ---

function detectPlatforms() {
  const platforms = [];

  // --- User-level platforms (global skills) ---

  const userLevel = [
    { name: "claude",       detect: join(HOME, ".claude"),                    skills: join(HOME, ".claude", "skills") },
    { name: "copilot",      detect: join(HOME, ".copilot"),                   skills: join(HOME, ".copilot", "skills") },
    { name: "cursor",       detect: join(HOME, ".cursor"),                    skills: join(HOME, ".cursor", "rules") },
    { name: "windsurf",     detect: join(HOME, ".codeium", "windsurf"),       skills: join(HOME, ".windsurf", "rules") },
    { name: "gemini",       detect: join(HOME, ".gemini"),                    skills: join(HOME, ".gemini", "skills") },
    { name: "codex",        detect: join(HOME, ".codex"),                     skills: join(HOME, ".codex", "skills") },
    { name: "goose",        detect: join(HOME, ".config", "goose"),           skills: join(HOME, ".config", "goose", "skills") },
    { name: "opencode",     detect: join(HOME, ".config", "opencode"),        skills: join(HOME, ".config", "opencode", "skills") },
  ];

  for (const { name, detect, skills } of userLevel) {
    if (existsSync(detect)) {
      platforms.push({ name, skills, level: "user" });
    }
  }

  // Cline is a VS Code extension — detect by extension directory
  const vscodeExtDir = join(HOME, ".vscode", "extensions");
  if (existsSync(vscodeExtDir)) {
    try {
      const entries = execSync(`ls "${vscodeExtDir}"`, { stdio: ["pipe", "pipe", "pipe"] })
        .toString().trim().split(/\r?\n/);
      if (entries.some(e => e.startsWith("saoudrizwan.claude-dev"))) {
        // Cline uses project-level .clinerules/ — add a user-level fallback
        const clineGlobal = IS_WIN
          ? join(HOME, "Documents", "Cline", "Rules")
          : join(HOME, "Documents", "Cline", "Rules");
        platforms.push({ name: "cline", skills: clineGlobal, level: "user" });
      }
    } catch { /* ignore */ }
  }

  // --- Project-level platforms (only if we're in a project directory) ---

  const projectLevel = [
    { name: "copilot (project)",  detect: ".github",      skills: join(".github", "skills") },
    { name: "cursor (project)",   detect: ".cursor",      skills: join(".cursor", "rules") },
    { name: "windsurf (project)", detect: ".windsurf",    skills: join(".windsurf", "rules") },
    { name: "cline (project)",    detect: ".clinerules",  skills: ".clinerules" },
  ];

  for (const { name, detect, skills } of projectLevel) {
    if (existsSync(detect)) {
      platforms.push({ name, skills, level: "project" });
    }
  }

  // VS Code detection (if Copilot is available but ~/.copilot doesn't exist yet)
  if (!platforms.some(p => p.name.startsWith("copilot"))) {
    const hasVSCode = which("code") !== null ||
      (osPlatform() === "darwin" && existsSync("/Applications/Visual Studio Code.app"));
    if (hasVSCode) {
      platforms.push({
        name: "copilot",
        skills: join(HOME, ".copilot", "skills"),
        level: "user",
      });
    }
  }

  // Default to Claude Code if nothing detected
  if (platforms.length === 0) {
    platforms.push({
      name: "claude",
      skills: join(HOME, ".claude", "skills"),
      level: "user",
    });
  }

  return platforms;
}

// --- Git clone helper ---

function gitClone(url, dest) {
  if (DRY_RUN) {
    info(`would clone: ${url} → ${dest}`);
    return true;
  }
  try {
    execSync(`git clone --depth 1 "${url}" "${dest}"`, {
      stdio: ["pipe", "pipe", "pipe"],
      timeout: 120_000,
    });
    return true;
  } catch (e) {
    const stderr = e.stderr ? e.stderr.toString().trim() : e.message;
    fail(`git clone failed: ${stderr}`);
    return false;
  }
}

// --- Link/copy helper (cross-platform) ---

function linkOrCopy(src, dest, name) {
  if (DRY_RUN) {
    info(`would install: ${name} → ${dest}`);
    return;
  }

  mkdirSync(dirname(dest), { recursive: true });

  // Remove existing
  if (existsSync(dest)) {
    try {
      const stat = lstatSync(dest);
      if (stat.isSymbolicLink()) {
        rmSync(dest);
      } else {
        rmSync(dest, { recursive: true, force: true });
      }
    } catch { /* ignore */ }
  }

  // Try symlink first
  try {
    symlinkSync(src, dest, "junction"); // "junction" is Windows-compatible, ignored on Unix
    ok(`${name} → ${dest} (symlink)`);
    return;
  } catch { /* fall through */ }

  // Fallback: copy
  try {
    cpSync(src, dest, { recursive: true });
    ok(`${name} → ${dest} (copy)`);
  } catch (e) {
    fail(`Could not install ${name}: ${e.message}`);
  }
}

// --- Uninstall ---

function uninstall(platforms) {
  header("Uninstalling cliskill");
  const names = ["cliskill", "clarity", "agent-skill-creator"];

  for (const { name: platName, skills } of platforms) {
    for (const skillName of names) {
      const dest = join(skills, skillName);
      if (existsSync(dest)) {
        if (DRY_RUN) {
          info(`would remove: ${dest}`);
        } else {
          try {
            rmSync(dest, { recursive: true, force: true });
            ok(`removed ${skillName} from ${platName}`);
          } catch (e) {
            fail(`could not remove ${dest}: ${e.message}`);
          }
        }
      }
    }
  }
}

// --- Install ---

function install(platforms) {
  // Separate user-level and project-level platforms
  const userPlatforms = platforms.filter(p => p.level === "user");
  const projectPlatforms = platforms.filter(p => p.level === "project");

  // Pick the primary user-level platform for cloning (first detected)
  const primary = userPlatforms[0] || platforms[0];
  const skillNames = ["cliskill", ...Object.keys(DEPS)];

  // Step 1: Clone all skills to primary platform
  header(`Installing to ${primary.name} (${primary.skills})`);

  const allSkills = [
    { name: "cliskill", url: REPO_URL },
    ...Object.entries(DEPS).map(([name, url]) => ({ name, url })),
  ];

  for (const { name, url } of allSkills) {
    const dest = join(primary.skills, name);
    if (existsSync(join(dest, "SKILL.md"))) {
      ok(`/${name} already installed`);
    } else {
      if (gitClone(url, dest)) {
        ok(`/${name} installed`);
      } else {
        if (name === "cliskill") {
          fail("Could not install cliskill. Check your network and git configuration.");
          process.exit(1);
        }
        warn(`/${name} could not be auto-installed. Install manually:`);
        console.log(`      git clone ${url} "${dest}"`);
      }
    }
  }

  // Step 2: Link/copy to additional user-level platforms
  const extraUser = userPlatforms.slice(1);
  if (extraUser.length > 0) {
    header("Linking to other platforms");
    for (const plat of extraUser) {
      for (const name of skillNames) {
        const src = join(primary.skills, name);
        const dest = join(plat.skills, name);
        if (existsSync(src) && !existsSync(dest)) {
          linkOrCopy(src, dest, `${name} → ${plat.name}`);
        } else if (existsSync(dest)) {
          ok(`${name} → ${plat.name} (already exists)`);
        }
      }
    }
  }

  // Step 3: Link/copy to project-level platforms
  if (projectPlatforms.length > 0) {
    header("Linking to project-level platforms");
    for (const plat of projectPlatforms) {
      for (const name of skillNames) {
        const src = join(primary.skills, name);
        const dest = join(plat.skills, name);
        if (existsSync(src) && !existsSync(dest)) {
          linkOrCopy(src, dest, `${name} → ${plat.name}`);
        } else if (existsSync(dest)) {
          ok(`${name} → ${plat.name} (already exists)`);
        }
      }
    }
  }
}

// --- Summary ---

function printSummary(platforms) {
  const userPlats = platforms.filter(p => p.level === "user").map(p => p.name);
  const projPlats = platforms.filter(p => p.level === "project").map(p => p.name);

  header("Installation complete");
  console.log();
  if (userPlats.length) console.log(`  User-level:    ${userPlats.join(", ")}`);
  if (projPlats.length) console.log(`  Project-level: ${projPlats.join(", ")}`);
  console.log(`
  ${BOLD}To use cliskill:${RESET}
  Open a new agent session and type:

    /cliskill https://api.example.com/docs

  ${BOLD}What it does:${RESET}
  Takes API references → produces a verified CLI skill that AI agents
  fully understand: how to use it, when to use it, when not to,
  and when to give up.

  ${BOLD}Docs:${RESET} https://github.com/FrancyJGLisboa/cliskill
`);
}

// --- Main ---

console.log(`\n${BOLD}cliskill installer${RESET}`);
console.log(`${"─".repeat(40)}`);

if (DRY_RUN) {
  warn("Dry run — no changes will be made\n");
}

// Check prerequisites
if (!UNINSTALL) {
  const prereqsOk = checkPrereqs();
  if (!prereqsOk) {
    console.log(`\n${RED}Prerequisites missing. Install them and try again.${RESET}\n`);
    process.exit(1);
  }
}

// Detect platforms
header("Detecting platforms");
const platforms = detectPlatforms();
for (const p of platforms) {
  ok(`${p.name}: ${p.skills}`);
}

// Install or uninstall
if (UNINSTALL) {
  uninstall(platforms);
  if (!DRY_RUN) ok("cliskill uninstalled.");
} else {
  install(platforms);
  if (!DRY_RUN) printSummary(platforms);
}

if (DRY_RUN) {
  console.log(`\n${YELLOW}Dry run complete. No changes were made.${RESET}\n`);
}
