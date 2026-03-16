#!/usr/bin/env python3
"""MCP bridge for cliskill — exposes the pipeline as tools any MCP client can call.

This server is a bridge, not a reimplementation. Each tool extracts the relevant
section from SKILL.md at runtime and returns it as instructions for the calling
agent to execute. SKILL.md remains the single source of truth.
"""

import os
import re

from fastmcp import FastMCP

SKILL_MD_PATH = os.path.join(os.path.dirname(__file__), "..", "SKILL.md")
REFS_DIR = os.path.join(os.path.dirname(__file__), "..", "references")

mcp = FastMCP(
    "cliskill",
    instructions=(
        "cliskill builds verified CLI skills from reference material. "
        "Use the cliskill_pipeline prompt to understand the workflow, "
        "then call tools in order: vibe → specify → build → verify → deploy."
    ),
)


def _read_skill_md() -> str:
    with open(SKILL_MD_PATH, "r") as f:
        return f.read()


def _extract_section(content: str, header_pattern: str) -> str:
    """Extract text from a ## header matching the pattern to the next ## header."""
    pattern = rf"(^## {header_pattern}.*?)(?=^## |\Z)"
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
    if match:
        return match.group(1).strip()
    return f"Section matching '{header_pattern}' not found in SKILL.md"


def _extract_sections(content: str, *patterns: str) -> str:
    """Extract multiple sections and join them."""
    parts = []
    for p in patterns:
        section = _extract_section(content, p)
        if not section.startswith("Section matching"):
            parts.append(section)
    return "\n\n---\n\n".join(parts)


def _read_reference(filename: str) -> str:
    path = os.path.join(REFS_DIR, filename)
    if os.path.isfile(path):
        with open(path, "r") as f:
            return f.read()
    return ""


# --- Prompt: pipeline overview ---


@mcp.prompt()
def cliskill_pipeline() -> str:
    """Overview of the cliskill pipeline — read this first to understand the workflow."""
    content = _read_skill_md()
    trigger = _extract_section(content, "Trigger")
    principles = _extract_section(content, "Core Principles")
    detection = _extract_section(content, "Phase Detection")
    return f"""# cliskill Pipeline Overview

{trigger}

{principles}

{detection}

## Tool Calling Order

For a standard build:
1. `cliskill_vibe` — capture success checks from the user's request
2. `cliskill_specify` — generate spec and holdout scenarios
3. `cliskill_build` — build the skill from the spec
4. `cliskill_verify` — run holdout scenarios, enter repair loop if needed
5. `cliskill_deploy` — deploy to detected platforms

For self-improvement: call `cliskill_self_improve` independently.
"""


# --- Tools ---


@mcp.tool()
def cliskill_vibe(user_request: str, references: list[str] | None = None) -> str:
    """Convert a user's request into 3-5 binary success checks (the vibe contract).

    Call this FIRST before any other cliskill tool. Pass the user's raw request
    and any reference paths/URLs. Returns instructions for the VIBE phase.

    Args:
        user_request: The user's raw description of what they want to build.
        references: Optional list of reference file paths or URLs.
    """
    content = _read_skill_md()
    vibe_section = _extract_section(content, "Phase V: VIBE")
    detect_section = _extract_section(content, "Phase Detection")

    context = f"## User Request\n\n{user_request}\n\n"
    if references:
        context += f"## References\n\n" + "\n".join(f"- {r}" for r in references) + "\n\n"

    return context + vibe_section + "\n\n---\n\n" + detect_section


@mcp.tool()
def cliskill_specify(vibe_contract_path: str = "", references: list[str] | None = None) -> str:
    """Generate a structured spec and holdout scenarios from references.

    Call after cliskill_vibe. Delegates to /clarity. Returns the SPECIFY phase
    instructions including the review gate logic.

    Args:
        vibe_contract_path: Path to the vibe contract file (.cliskill/vibe-contract.md).
        references: List of reference file paths or URLs to pass to /clarity.
    """
    content = _read_skill_md()
    section = _extract_section(content, "Phase 1: SPECIFY")

    context = ""
    if vibe_contract_path:
        context += f"## Vibe Contract\n\nPath: {vibe_contract_path}\n\n"
    if references:
        context += f"## References\n\n" + "\n".join(f"- {r}" for r in references) + "\n\n"

    return context + section


@mcp.tool()
def cliskill_build(skill_brief_path: str = "", loop_count: int = 0) -> str:
    """Build the skill from the spec. Delegates to /agent-skill-creator.

    Call after cliskill_specify (or after cliskill_verify in a repair loop).
    Returns BUILD phase instructions including eval harness generation.

    Args:
        skill_brief_path: Path to the skill brief (.clarity/skill-brief.md).
        loop_count: Current repair loop count (0 for first build).
    """
    content = _read_skill_md()
    section = _extract_section(content, "Phase 2: BUILD")

    context = ""
    if skill_brief_path:
        context += f"## Skill Brief\n\nPath: {skill_brief_path}\n\n"
    if loop_count > 0:
        context += f"## Rebuild\n\nThis is rebuild #{loop_count}. Read .cliskill/loop-{loop_count}/changes.md for context.\n\n"

    return context + section


@mcp.tool()
def cliskill_verify(skill_path: str = "", scenario_dir: str = "scenarios/") -> str:
    """Run holdout scenarios against the built skill. Enter repair loop if failures.

    Call after cliskill_build. Returns VERIFY + REPAIR LOOP + ESCALATION instructions.

    Args:
        skill_path: Path to the built skill directory.
        scenario_dir: Path to the holdout scenarios directory.
    """
    content = _read_skill_md()
    verify = _extract_section(content, "Phase 3: VERIFY")
    repair = _extract_section(content, "REPAIR LOOP")
    escalation = _extract_section(content, "Guided Escalation")

    # Also load reference files the agent needs during verification
    eval_router = _read_reference("evaluation-router.md")
    loop_protocol = _read_reference("loop-protocol.md")

    context = ""
    if skill_path:
        context += f"## Skill Path\n\n{skill_path}\n\n"
    context += f"## Scenario Directory\n\n{scenario_dir}\n\n"

    parts = [context, verify, repair, escalation]
    if eval_router:
        parts.append(f"---\n\n# Reference: Evaluation Router\n\n{eval_router}")
    if loop_protocol:
        parts.append(f"---\n\n# Reference: Loop Protocol\n\n{loop_protocol}")

    return "\n\n".join(parts)


@mcp.tool()
def cliskill_deploy(skill_path: str = "", skill_name: str = "") -> str:
    """Deploy the verified skill to detected platforms and log build metrics.

    Call after cliskill_verify succeeds. Returns DEPLOY phase instructions.

    Args:
        skill_path: Path to the verified skill directory.
        skill_name: Name of the skill being deployed.
    """
    content = _read_skill_md()
    section = _extract_section(content, "Phase 4: DEPLOY")

    context = ""
    if skill_path:
        context += f"## Skill Path\n\n{skill_path}\n\n"
    if skill_name:
        context += f"## Skill Name\n\n{skill_name}\n\n"

    return context + section


@mcp.tool()
def cliskill_self_improve() -> str:
    """Analyze cliskill's build metrics and propose improvements to its own instructions.

    Call independently — not part of the standard build pipeline.
    Requires at least 5 builds in .cliskill-meta/results.tsv.
    """
    content = _read_skill_md()
    section = _extract_section(content, "Phase S: SELF-IMPROVE")
    protocol = _read_reference("self-improvement-protocol.md")

    parts = [section]
    if protocol:
        parts.append(f"---\n\n# Reference: Self-Improvement Protocol\n\n{protocol}")

    return "\n\n".join(parts)


if __name__ == "__main__":
    mcp.run()
