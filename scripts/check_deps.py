#!/usr/bin/env python3
"""Check that cliskill's dependencies (/clarity and /agent-skill-creator) are installed.

If missing, auto-detect the user's platform and install them automatically.
"""

import os
import shutil
import subprocess
import sys

# Source repos for dependencies
DEPENDENCY_REPOS = {
    "clarity": "https://github.com/FrancyJGLisboa/clarity",
    "agent-skill-creator": "https://github.com/FrancyJGLisboa/agent-skill-creator",
}

# Platform detection: ordered by priority
# Each entry: (platform_name, base_skills_dir, detection_path)
#
# User-level platforms (global skills)
PLATFORMS = [
    ("claude",            os.path.expanduser("~/.claude/skills"),            os.path.expanduser("~/.claude")),
    ("copilot",           os.path.expanduser("~/.copilot/skills"),           os.path.expanduser("~/.copilot")),
    ("cursor",            os.path.expanduser("~/.cursor/rules"),             os.path.expanduser("~/.cursor")),
    ("windsurf",          os.path.expanduser("~/.windsurf/rules"),           os.path.expanduser("~/.codeium/windsurf")),
    ("gemini",            os.path.expanduser("~/.gemini/skills"),            os.path.expanduser("~/.gemini")),
    ("codex",             os.path.expanduser("~/.codex/skills"),             os.path.expanduser("~/.codex")),
    ("goose",             os.path.expanduser("~/.config/goose/skills"),      os.path.expanduser("~/.config/goose")),
    ("opencode",          os.path.expanduser("~/.config/opencode/skills"),   os.path.expanduser("~/.config/opencode")),
    # Vendor-neutral
    ("agents (user)",     os.path.expanduser("~/.agents/skills"),            os.path.expanduser("~/.agents")),
    # Project-level platforms (detected from cwd)
    ("agents (project)",  os.path.join(".agents", "skills"),                 ".agents"),
    ("copilot (project)", os.path.join(".github", "skills"),                 ".github"),
    ("cursor (project)",  os.path.join(".cursor", "rules"),                  ".cursor"),
    ("windsurf (project)", os.path.join(".windsurf", "rules"),               ".windsurf"),
    ("cline (project)",   ".clinerules",                                     ".clinerules"),
]

REQUIRED_SKILLS = ["clarity", "agent-skill-creator"]


def _is_link_or_junction(path):
    """Check if path is a symlink or Windows junction."""
    if os.path.islink(path):
        return True
    if os.name == "nt" and os.path.isdir(path):
        import ctypes
        FILE_ATTRIBUTE_REPARSE_POINT = 0x0400
        attrs = ctypes.windll.kernel32.GetFileAttributesW(str(path))
        return attrs != -1 and (attrs & FILE_ATTRIBUTE_REPARSE_POINT)
    return False


def detect_platforms():
    """Return list of (platform_name, skills_dir) for all detected platforms."""
    detected = []
    for name, skills_dir, detect_path in PLATFORMS:
        if os.path.isdir(detect_path):
            detected.append((name, skills_dir))
    return detected


def find_skill(name, platforms=None):
    """Return list of (platform, path) where this skill is installed."""
    if platforms is None:
        platforms = detect_platforms()
    found = []
    for platform, base in platforms:
        skill_path = os.path.join(base, name)
        skill_md = os.path.join(skill_path, "SKILL.md")
        if os.path.isfile(skill_md):
            found.append((platform, skill_path))
        elif _is_link_or_junction(skill_path):
            target = os.path.realpath(skill_path)
            if os.path.isfile(os.path.join(target, "SKILL.md")):
                found.append((platform, f"{skill_path} -> {target}"))
    return found


def has_git():
    """Check if git is available."""
    return shutil.which("git") is not None


def install_skill(name, platforms):
    """Auto-install a missing skill to all detected platforms."""
    repo_url = DEPENDENCY_REPOS.get(name)
    if not repo_url:
        print(f"  [error] No source repo known for /{name}")
        return False

    if not has_git():
        print(f"  [error] git is not installed. Cannot auto-install /{name}.")
        print(f"          Install git, then run: git clone {repo_url}")
        return False

    if not platforms:
        print(f"  [error] No supported platform detected. Cannot auto-install /{name}.")
        print(f"          Manually clone: git clone {repo_url} <your-skills-dir>/{name}")
        return False

    success = False
    for platform, skills_dir in platforms:
        dest = os.path.join(skills_dir, name)
        if os.path.isdir(dest):
            continue

        print(f"  Installing /{name} to {platform}: {dest}")
        os.makedirs(skills_dir, exist_ok=True)

        try:
            result = subprocess.run(
                ["git", "clone", "--depth", "1", repo_url, dest],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if result.returncode == 0:
                print(f"  [ok] /{name} installed to {dest}")
                success = True
                # Only install to the first detected platform
                break
            else:
                print(f"  [error] git clone failed: {result.stderr.strip()}")
        except subprocess.TimeoutExpired:
            print(f"  [error] git clone timed out for /{name}")
        except OSError as e:
            print(f"  [error] Failed to run git: {e}")

    return success


def main():
    all_ok = True
    platforms = detect_platforms()

    print("cliskill dependency check")
    print("=" * 40)

    if platforms:
        print(f"\nDetected platforms: {', '.join(p[0] for p in platforms)}")
    else:
        print("\nNo supported platforms detected.")

    print()

    for skill in REQUIRED_SKILLS:
        locations = find_skill(skill, platforms)
        if locations:
            print(f"  [ok] /{skill}")
            for platform, path in locations:
                print(f"       {platform}: {path}")
        else:
            print(f"  [missing] /{skill} — attempting auto-install...")
            installed = install_skill(skill, platforms)
            if installed:
                all_ok = True
            else:
                print(f"  [failed] Could not auto-install /{skill}")
                all_ok = False
        print()

    # MCP server availability (informational, not required)
    print("MCP bridge:")
    try:
        import importlib
        importlib.import_module("fastmcp")
        print("  [ok] fastmcp installed — MCP bridge available")
    except ImportError:
        # Also check if available via uv
        uv_available = shutil.which("uv") is not None
        if uv_available:
            result = subprocess.run(
                ["uv", "run", "python3", "-c", "import fastmcp"],
                capture_output=True, timeout=10,
            )
            if result.returncode == 0:
                print("  [ok] fastmcp installed (via uv) — MCP bridge available")
            else:
                print("  [info] fastmcp not installed — MCP bridge unavailable")
                print("         Install with: uv pip install fastmcp")
                print("         MCP is optional — SKILL.md works without it")
        else:
            print("  [info] fastmcp not installed — MCP bridge unavailable")
            print("         Install with: pip install fastmcp")
            print("         MCP is optional — SKILL.md works without it")
    print()

    if all_ok:
        print("All dependencies ready.")
        sys.exit(0)
    else:
        print("Some dependencies could not be installed automatically.")
        print()
        print("Manual install:")
        print(f"  /clarity:              git clone {DEPENDENCY_REPOS['clarity']}")
        print(f"  /agent-skill-creator:  git clone {DEPENDENCY_REPOS['agent-skill-creator']}")
        sys.exit(1)


if __name__ == "__main__":
    main()
