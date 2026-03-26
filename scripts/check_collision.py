#!/usr/bin/env python3
"""Check for activation namespace collisions before deploying a new skill.

Usage:
    python3 scripts/check_collision.py <new-skill-name>

Scans all installed skills in known platform paths, reads their SKILL.md
frontmatter for 'activation:' fields, and reports collisions.

Exit codes:
    0 = no collision
    1 = collision found (prints conflicting skill path)
    2 = usage error
"""

import sys
import re
from pathlib import Path

SKILL_DIRS = [
    Path.home() / ".agents" / "skills",
    Path.home() / ".claude" / "skills",
    Path.home() / ".copilot" / "skills",
    Path.home() / ".cursor" / "rules",
    Path.home() / ".windsurf" / "rules",
    Path.home() / ".gemini" / "skills",
    Path.home() / ".codex" / "skills",
    Path.home() / ".config" / "goose" / "skills",
    Path.home() / ".config" / "opencode" / "skills",
]


def extract_activation(skill_md_path: Path) -> str | None:
    """Extract 'activation: /name' from SKILL.md frontmatter."""
    try:
        text = skill_md_path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None

    in_frontmatter = False
    for line in text.splitlines():
        if line.strip() == "---":
            if not in_frontmatter:
                in_frontmatter = True
                continue
            else:
                break
        if in_frontmatter:
            m = re.match(r"^activation:\s*(/\S+)", line)
            if m:
                return m.group(1)
    return None


def find_all_activations() -> dict[str, str]:
    """Returns {activation_prefix: skill_path} for all installed skills."""
    activations = {}
    for skill_dir in SKILL_DIRS:
        if not skill_dir.exists():
            continue
        for entry in skill_dir.iterdir():
            skill_md = entry / "SKILL.md" if entry.is_dir() else None
            if skill_md and skill_md.exists():
                activation = extract_activation(skill_md)
                if activation:
                    activations[activation] = str(entry)
    return activations


def main():
    if len(sys.argv) < 2:
        print("Usage: check_collision.py <skill-name>", file=sys.stderr)
        sys.exit(2)

    new_name = sys.argv[1]
    new_activation = f"/{new_name}" if not new_name.startswith("/") else new_name

    existing = find_all_activations()

    if new_activation in existing:
        conflict_path = existing[new_activation]
        print(f'{{"collision": true, "activation": "{new_activation}", "conflicting_skill": "{conflict_path}"}}')
        sys.exit(1)
    else:
        print(f'{{"collision": false, "activation": "{new_activation}", "installed_skills": {len(existing)}}}')
        sys.exit(0)


if __name__ == "__main__":
    main()
