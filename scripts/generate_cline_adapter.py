#!/usr/bin/env python3
"""Generate a Cline workflow adapter from cliskill's SKILL.md.

Cline doesn't support SKILL.md natively. It uses .clinerules/workflows/*.md
files invokable as slash commands. This script generates a thin adapter that
tells Cline's agent to read and follow SKILL.md.

Usage:
    python3 scripts/generate_cline_adapter.py <cliskill-repo-path> [output-dir]

If output-dir is omitted, writes to .clinerules/workflows/ in the current directory.
"""

import os
import sys
import textwrap


def generate(repo_path: str, output_dir: str | None = None) -> str:
    skill_md_path = os.path.join(repo_path, "SKILL.md")
    if not os.path.isfile(skill_md_path):
        print(f"Error: SKILL.md not found at {skill_md_path}", file=sys.stderr)
        sys.exit(1)

    if output_dir is None:
        output_dir = os.path.join(".", ".clinerules", "workflows")

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "cliskill.md")

    content = textwrap.dedent(f"""\
        # cliskill — Build Verified CLI Skills

        Build verified, cross-platform CLI skills from any reference material.
        Use when the user wants to turn API docs, repos, PDFs, or course materials
        into agent-friendly CLI tools.

        ## Instructions

        1. Read the cliskill SKILL.md file at `{skill_md_path}`
        2. Follow the complete pipeline protocol defined in SKILL.md:
           - **Phase V: VIBE** — capture 3-5 binary success checks from the user
           - **Phase Detection** — infer the right mode (standard, discover, research, update)
           - **Phase 1: SPECIFY** — delegate to /clarity for spec and holdout scenarios
           - **Phase 2: BUILD** — delegate to /agent-skill-creator
           - **Phase 3: VERIFY** — run holdout scenarios, repair loop if needed
           - **Phase 4: DEPLOY** — deploy to detected platforms
        3. Load reference files from `{os.path.join(repo_path, 'references')}` on demand as SKILL.md instructs
        4. Write pipeline state to `.cliskill/` in the current working directory

        ## Dependencies

        This workflow requires two sub-skills: /clarity and /agent-skill-creator.
        Run `python3 {os.path.join(repo_path, 'scripts', 'check_deps.py')}` to verify they are installed.

        ## Trigger

        Use this workflow when the user asks to:
        - Build a CLI skill from API docs, repos, or reference material
        - Turn documentation into an agent-friendly tool
        - Create a verified, cross-platform CLI wrapper
        - Discover what analytics are possible from a repo + knowledge source
        - Optimize a model or pipeline metric continuously
    """)

    with open(output_path, "w") as f:
        f.write(content)

    print(f"  Generated: {output_path}")
    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <cliskill-repo-path> [output-dir]", file=sys.stderr)
        sys.exit(1)

    repo = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else None
    generate(repo, out)
