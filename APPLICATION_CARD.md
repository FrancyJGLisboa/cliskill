# Application Card: cliskill

## Problem

AI agents need to use APIs. The naive approach is to load API documentation into the agent's context window. This doesn't scale.

A single API reference can consume 50,000+ tokens. Two or three APIs and the agent has burned its context window before it starts reasoning. The agent becomes slow, expensive, and confused — drowning in endpoint specifications when it should be solving the user's problem.

The deeper issue: **agents don't need to understand APIs. They need to understand tools.**

A human developer reads API docs once, builds a mental model, and then works from that model — not by re-reading the docs on every call. Agents should work the same way, but they can't build persistent mental models across sessions. Every conversation starts from zero.

## Solution

cliskill compresses API documentation into CLI tools that agents can wield without understanding the underlying API.

```
Raw API docs (50,000+ tokens)
    → clarity extracts what matters
Verified spec + holdout scenarios
    → agent-skill-creator builds the CLI
SKILL.md (~300 lines) + scripts (agent never reads)
    → agent activates the skill in ~500 tokens
```

The result is a CLI skill where:

- The **SKILL.md** tells the agent what commands exist, when to use them, and when not to (~300 lines, loaded only when relevant)
- The **scripts/** contain the actual API logic (the agent calls them, never reads them)
- The **anti-goals** tell the agent what to honestly refuse
- The **error handling** tells the agent how to fail gracefully

A 50,000-token API reference becomes a 500-token tool activation. The agent spends its context on reasoning, not on understanding its tools.

## Why CLI

CLI is the universal interface for agent tooling. Every major agent platform — Claude Code, Copilot, Gemini CLI, Codex, Cursor, Goose — can execute shell commands. No SDK integration, no plugin API, no platform-specific adapter.

A CLI skill works everywhere because:

1. **Execution is trivial.** The agent runs a shell command and reads stdout.
2. **Interfaces are self-documenting.** `--help`, structured output, exit codes.
3. **Composition is natural.** Agents can pipe, chain, and combine CLI tools the same way humans do.
4. **Isolation is free.** The skill runs in its own process. No shared state, no dependency conflicts, no context pollution.

## Why "Agent-Friendly" Matters

A traditional CLI tool is designed for humans. An agent-friendly CLI skill is designed for agents. The difference:

| Aspect | Human CLI | Agent-Friendly Skill |
|--------|-----------|---------------------|
| **Discovery** | `man` pages, README | SKILL.md with activation triggers — the agent knows *when* to reach for this tool based on user intent |
| **Scope** | Feature-rich, many flags | Focused on the 80% path — 4-6 analyses, not 40 endpoints |
| **Limitations** | Implied, learned through experience | Explicit anti-goals — the agent knows what *not* to attempt |
| **Failure** | Stack traces, error codes | Guided failure — the agent knows what to tell the user and what to try next |
| **Context cost** | Irrelevant to humans | Minimal activation footprint — metadata first, full instructions only when needed |

The critical property: **an agent reading only the SKILL.md should be able to use the tool correctly, know its limits, and fail gracefully.** If the agent needs to read the source code or API docs to use the skill, the skill has failed.

## The Verification Gap

Generating CLI wrappers around APIs is easy. Generating CLI wrappers that *actually work correctly* is hard. The gap between "code that looks right" and "code that handles edge cases" is where most auto-generated tools fail silently.

cliskill closes this gap with a **holdout evaluation loop**:

1. `/clarity` generates a spec and holdout test scenarios from the API docs
2. `/agent-skill-creator` builds the CLI skill from the spec
3. The skill is tested against the holdout scenarios — scenarios the builder never saw
4. Failures are classified (spec gap? implementation gap? test gap?) and auto-fixed
5. Repeat until all scenarios pass, or escalate to a human

The holdout separation is architecturally load-bearing. The builder never sees the test scenarios. If it could, it would optimize for passing tests rather than implementing the spec correctly. This is the same principle behind train/test splits in ML — and it's why cliskill never auto-fixes failing tests. If the test is wrong, only a human should change it.

## Distribution

cliskill is distributed as an npm package for cross-platform one-command installation:

```bash
npx cliskill
```

The installer handles the full onboarding flow:

1. **Prerequisite check** — verifies git and Python 3.10+ are available. If missing, prints OS-specific install guidance (e.g., `brew install git` on macOS, `winget install Git.Git` on Windows, `sudo apt install git` on Linux).
2. **Platform detection** — auto-detects AI coding tools at two levels:
   - **User-level** (global): Claude Code, VS Code + Copilot, Cursor, Windsurf, Gemini CLI, Codex, Goose, OpenCode
   - **Project-level** (per-repo): GitHub Copilot (`.github/`), Cursor (`.cursor/`), Windsurf (`.windsurf/`), Cline (`.clinerules/`)
   - Installs to **all** detected platforms simultaneously — a developer using both VS Code and Claude Code gets both.
3. **Dependency installation** — clones `/clarity` and `/agent-skill-creator` into the primary platform's skill directory, then symlinks to others. No manual setup.
4. **Cross-OS compatibility** — on Windows, falls back from symlinks to directory junctions (no admin required) to copy as a last resort. All three installers (Node.js, Bash, PowerShell) cover the same platform matrix.

A user on a fresh machine with Node.js, git, and Python goes from zero to working `/cliskill` in one command. Dependencies are also auto-installed at runtime via `check_deps.py` if somehow missing after install — defense in depth.

## Architecture

cliskill is a conductor, not an orchestra. It orchestrates two independent skills:

- **`/clarity`** — Reads messy references, produces verified specifications and holdout scenarios
- **`/agent-skill-creator`** — Takes specifications, produces deployed CLI skills on 14+ platforms

Neither skill has an evaluation-fix-rebuild loop. cliskill adds that loop — the piece that turns "generate once and hope" into "generate, verify, fix, verify again."

```
Human provides API references
         ↓
    ┌─────────┐
    │ SPECIFY │  ← /clarity (ingest, spec, scenarios, handoff)
    └────┬────┘
         ↓
   [Review Gate 1]  ← Human approves spec
         ↓
    ┌─────────┐
    │  BUILD  │  ← /agent-skill-creator (architecture, detection, implementation)
    └────┬────┘
         ↓
    ┌─────────┐
    │ VERIFY  │  ← /clarity evaluate (holdout scenarios)
    └────┬────┘
         ↓
     Pass? ──yes──→ [Review Gate 2] → DEPLOY
         │
         no
         ↓
    ┌──────────┐
    │  REPAIR  │  classify failure → fix spec or code → rebuild
    └────┬─────┘
         ↓
      (back to BUILD, max 3 loops)
```

The human touches the pipeline twice: approving the spec, and approving the deployment. Everything between is autonomous.

## Relationship to agent-skill-creator

cliskill is the successor to `/agent-skill-creator`, not a wrapper around it.

`/agent-skill-creator` is an open-loop generator. It takes a spec (or raw references), builds a skill, runs validation and a security scan, and ships it. If the generated skill misunderstands an API's pagination, silently drops error cases, or implements the wrong business logic — nobody finds out until a human or an agent hits the bug in production. There is no verification step. Build and hope.

This is the same gap that separates a code generator from a compiler. A code generator produces output. A compiler produces output *and tells you if it's wrong*. cliskill adds the "tells you if it's wrong" part — and then fixes it.

The evolution is concrete:

| Capability | agent-skill-creator | cliskill |
|---|---|---|
| Reads API docs | Yes (Phase 1) | Yes (via /clarity) |
| Generates skill code | Yes (Phase 5) | Yes (via /agent-skill-creator) |
| Validates structure | Yes (SKILL.md schema) | Yes (inherited) |
| Security scans | Yes (pattern matching) | Yes (inherited) |
| **Verifies behavior** | No | Yes — holdout scenarios |
| **Classifies failures** | No | Yes — spec gap vs impl gap vs test gap |
| **Auto-fixes and rebuilds** | No | Yes — up to 3 loops |
| **Knows when to give up** | No — always ships | Yes — escalates with diagnostics |
| **Spec-first workflow** | Optional — can skip to build | Mandatory — /clarity produces verified spec before build |

The critical difference is the last row. agent-skill-creator *can* skip the spec and build directly from raw references. This is fast but fragile — the skill reflects whatever the LLM inferred from the docs, with no structured verification. cliskill forces the spec-first path: clarity extracts, structures, and creates holdout tests *before* the builder ever sees the brief. The builder implements against a verified spec, not against raw inference.

agent-skill-creator remains excellent at what it does — it's the best skill builder available. But it's a build tool, not a factory. cliskill turns it into a factory by adding the quality loop that build tools lack.

Both projects stay independent. agent-skill-creator continues to evolve as the implementation engine. cliskill orchestrates it within a closed-loop pipeline where "it compiled" is no longer sufficient — "it works correctly against scenarios the builder never saw" is the bar.

## Scope and Limitations

**cliskill is good at:**
- APIs with documentation (REST, GraphQL, well-documented libraries)
- Tools with clear input/output contracts
- Skills that can be expressed as CLI commands with structured output

**cliskill is not designed for:**
- Real-time streaming APIs (WebSockets, SSE) — CLI is request/response
- APIs requiring complex OAuth flows with browser redirects — needs human setup
- Skills that require persistent state across invocations — CLI is stateless by design
- Replacing human judgment on spec review — the two review gates exist for a reason

## Metrics That Matter

For a cliskill-produced skill, the quality signals are:

- **Holdout pass rate**: Did the skill pass scenarios the builder never saw?
- **Activation precision**: Does the agent reach for this skill at the right time and avoid it at the wrong time?
- **Context cost**: How many tokens does the agent spend to activate and use the skill?
- **Failure honesty**: When the skill can't help, does the agent say so clearly?

## Links

- **Install**: `npx cliskill`
- **Repository**: [github.com/FrancyJGLisboa/cliskill](https://github.com/FrancyJGLisboa/cliskill)
- **npm**: [npmjs.com/package/cliskill](https://www.npmjs.com/package/cliskill)
- **Dependency — /clarity**: [github.com/FrancyJGLisboa/clarity](https://github.com/FrancyJGLisboa/clarity)
- **Dependency — /agent-skill-creator**: [github.com/FrancyJGLisboa/agent-skill-creator](https://github.com/FrancyJGLisboa/agent-skill-creator)

## License

MIT
