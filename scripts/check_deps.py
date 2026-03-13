#!/usr/bin/env python3
"""Check that cliskill's dependencies (/clarity and /agent-skill-creator) are installed."""

import os
import sys

SKILL_DIRS = {
    "claude": os.path.expanduser("~/.claude/skills"),
    "copilot": os.path.expanduser("~/.copilot/skills"),
    "universal": os.path.expanduser("~/.agents/skills"),
    "gemini": os.path.expanduser("~/.gemini/skills"),
    "goose": os.path.expanduser("~/.config/goose/skills"),
    "opencode": os.path.expanduser("~/.config/opencode/skills"),
}

REQUIRED_SKILLS = ["clarity", "agent-skill-creator"]


def _is_link_or_junction(path):
    """Check if path is a symlink or Windows junction."""
    if os.path.islink(path):
        return True
    # Windows junctions aren't detected by islink — check reparse point attribute
    if os.name == "nt" and os.path.isdir(path):
        import ctypes
        FILE_ATTRIBUTE_REPARSE_POINT = 0x0400
        attrs = ctypes.windll.kernel32.GetFileAttributesW(str(path))
        return attrs != -1 and (attrs & FILE_ATTRIBUTE_REPARSE_POINT)
    return False


def find_skill(name):
    """Return list of (platform, path) where this skill is installed."""
    found = []
    for platform, base in SKILL_DIRS.items():
        skill_path = os.path.join(base, name)
        skill_md = os.path.join(skill_path, "SKILL.md")
        if os.path.isfile(skill_md):
            found.append((platform, skill_path))
        elif _is_link_or_junction(skill_path):
            target = os.path.realpath(skill_path)
            if os.path.isfile(os.path.join(target, "SKILL.md")):
                found.append((platform, f"{skill_path} -> {target}"))
    return found


def main():
    all_ok = True

    print("cliskill dependency check")
    print("=" * 40)
    print()

    for skill in REQUIRED_SKILLS:
        locations = find_skill(skill)
        if locations:
            print(f"  [ok] /{skill}")
            for platform, path in locations:
                print(f"       {platform}: {path}")
        else:
            print(f"  [missing] /{skill}")
            all_ok = False
        print()

    if all_ok:
        print("All dependencies found.")
        sys.exit(0)
    else:
        print("Missing dependencies. Install them before running /cliskill.")
        print()
        print("  /clarity:              https://github.com/FrancyJGLisboa/clarity")
        print("  /agent-skill-creator:  https://github.com/FrancyJGLisboa/agent-skill-creator")
        sys.exit(1)


if __name__ == "__main__":
    main()
