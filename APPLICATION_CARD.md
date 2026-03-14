# Application Card: cliskill

> Your agents don't need to read the docs. They need a tool that already did.

![cliskill — Self-Bootstrapping CLI Skills for AI Agents](cliskill.png)

## Problem

AI agents need tools. The naive approach is to load documentation into the agent's context window — API references, library docs, course materials, repo READMEs. This doesn't scale.

A single API reference can consume 50,000+ tokens. A repo with methodology docs can exceed 100,000. The agent burns its context window before it starts reasoning — slow, expensive, and confused.

The deeper issue: **agents don't need to understand documentation. They need tools they can wield.**

A human developer reads docs once, builds a mental model, and works from that model. Agents can't build persistent mental models across sessions. Every conversation starts from zero. And even if the agent understands the docs, the user still needs to install dependencies, configure environments, and debug setup issues before the first query runs.

## Solution

cliskill turns any reference material — API docs, repositories, PDFs, course materials, pasted text — into **self-bootstrapping CLI tools** that AI agents can wield on any platform, on any OS, without setup.

The produced skills are git repositories. The user experience:

```bash
git clone <skill-repo>
cd <skill>
./skill-name <command>        # macOS/Linux — auto-installs deps on first run
.\skill-name.ps1 <command>    # Windows PowerShell — same
```

No `pip install`, no environment setup, no configuration. Clone and run.

Three entry points, one pipeline:

```
1. API docs → CLI skill (standard)
   Raw API docs (50,000+ tokens)
       → clarity extracts what matters
   Verified spec + holdout scenarios
       → agent-skill-creator builds the CLI
   Self-bootstrapping skill repo
       → agent activates in ~500 tokens, user clones and runs

2. Repo + knowledge → analytics skill (discover)
   Repository code + course materials / methodology docs
       → cross-reference capabilities against methods
   Ranked feasibility report → user selects
       → pipeline builds, verifies, and packages the skill

3. Pipeline + metric → optimized model (research)
   ML pipeline + domain knowledge
       → negotiate metric, bootstrap eval harness
   Autonomous optimization loop (PROPOSE → RUN → CLASSIFY → KEEP/REVERT)
       → convergence detection, guided review, Pareto front
```

The result is a CLI skill where:

- The **SKILL.md** tells the agent what commands exist, when to use them, and when not to (~300 lines, loaded only when relevant)
- The **scripts/** contain the actual logic (the agent calls them, never reads them)
- The **anti-goals** tell the agent what to honestly refuse
- The **error handling** tells the agent how to fail gracefully
- The **wrappers** (`./skill` + `.\skill.ps1`) auto-bootstrap Python, uv, venv, and dependencies on first run — on any OS
- The **JSON output** to stdout is structured for agent consumption; errors go to stderr with exit code 1

A 50,000-token API reference becomes a 500-token tool activation. The agent spends its context on reasoning, not on understanding its tools. The user spends zero time on setup.

### Example: na-analytics

[na-analytics](https://github.com/FrancyJGLisboa/na-analytics) was built by cliskill's discover mode from a commodity price ETL repo + a professional trading course PDF. The result:

- **11 commands** — basis, PPE, futures curves, crush margins, breakeven, profitability matrices
- **Zero setup** — clones and runs, fetches live daily-updated data from GitHub
- **Verified** — 17 holdout scenarios, 3 known-answer tests from course material (exact match)
- **Cross-platform** — bash + PowerShell wrappers
- **Agent-tested** — Claude Code agents used it successfully on first try

```bash
$ git clone https://github.com/FrancyJGLisboa/na-analytics && cd na-analytics
$ ./na-analytics spread --commodity soja --indicator soja-mercado-fisico-sindicatos-e-cooperativas
{
  "summary": {"mean": 115.27, "min": 99.0, "max": 130.0, "count": 30},
  "extremes": {
    "lowest":  {"location": "Campo Novo do Parecis/MT", "price": 99.0},
    "highest": {"location": "Porto Santos/SP", "price": 130.0}
  }
}
```

From PDF course formulas to working CLI analytics — verified, self-installing, cross-platform.

## Why CLI

CLI is the universal interface for agent tooling. Every major agent platform — Claude Code, Copilot, Cursor, Windsurf, Gemini CLI, Codex, Goose, OpenCode, Cline — can execute shell commands. No SDK integration, no plugin API, no platform-specific adapter.

A CLI skill works everywhere because:

1. **Execution is trivial.** The agent runs a shell command and reads stdout.
2. **Interfaces are self-documenting.** `--help`, structured output, exit codes.
3. **Composition is natural.** Agents can pipe, chain, and combine CLI tools the same way humans do.
4. **Isolation is free.** The skill runs in its own process. No shared state, no dependency conflicts, no context pollution.

## Why "Agent-Friendly" Matters

A traditional CLI tool is designed for humans. An agent-friendly CLI skill is designed for agents. The difference:

| Aspect | Human CLI | Agent-Friendly Skill |
|--------|-----------|---------------------|
| **Setup** | `pip install`, configure, read docs | `git clone` → `./skill <command>` — auto-bootstraps on first run, any OS |
| **Discovery** | `man` pages, README | SKILL.md with activation triggers — the agent knows *when* to reach for this tool based on user intent |
| **Scope** | Feature-rich, many flags | Focused on the 80% path — 4-6 analyses, not 40 endpoints |
| **Limitations** | Implied, learned through experience | Explicit anti-goals — the agent knows what *not* to attempt |
| **Failure** | Stack traces, error codes | Guided failure — JSON errors to stderr with hints the agent can act on |
| **Output** | Human-readable text | Structured JSON to stdout — agents parse, don't regex |
| **Platform** | OS-specific installers | Bash + PowerShell wrappers — works on macOS, Linux, Windows |
| **Context cost** | Irrelevant to humans | Minimal activation footprint — metadata first, full instructions only when needed |

The critical properties: **an agent reading only the SKILL.md should be able to use the tool correctly, know its limits, and fail gracefully.** And **a user should go from zero to working queries in one command after clone.** If the agent needs to read source code, or the user needs to install dependencies manually, the skill has failed.

## The Verification Gap

Generating CLI wrappers around APIs is easy. Generating CLI wrappers that *actually work correctly* is hard. The gap between "code that looks right" and "code that handles edge cases" is where most auto-generated tools fail silently.

cliskill closes this gap with a **holdout evaluation loop**:

1. `/clarity` generates a spec and holdout test scenarios from the reference material
2. `/agent-skill-creator` builds the CLI skill from the spec
3. The skill is tested against the holdout scenarios — scenarios the builder never saw
4. Failures are classified (spec gap? implementation gap? test gap?) and auto-fixed
5. Repeat until all scenarios pass, or escalate to a human

The holdout separation is architecturally load-bearing. The builder never sees the test scenarios. If it could, it would optimize for passing tests rather than implementing the spec correctly. This is the same principle behind train/test splits in ML — and it's why cliskill never auto-fixes failing tests. If the test is wrong, only a human should change it.

## Distribution

cliskill is distributed via GitHub. Clone and run the installer:

```bash
git clone https://github.com/FrancyJGLisboa/cliskill
cd cliskill
./scripts/install.sh --with-deps    # macOS/Linux
.\scripts\install.ps1 -WithDeps     # Windows (PowerShell)
```

The installer handles the full onboarding flow:

1. **Prerequisite check** — verifies git and Python 3.10+ are available. If missing, prints OS-specific install guidance (e.g., `brew install git` on macOS, `winget install Git.Git` on Windows, `sudo apt install git` on Linux).
2. **Platform detection** — auto-detects AI coding tools at two levels:
   - **User-level** (global): Claude Code, VS Code + Copilot, Cursor, Windsurf, Gemini CLI, Codex, Goose, OpenCode
   - **Project-level** (per-repo): GitHub Copilot (`.github/`), Cursor (`.cursor/`), Windsurf (`.windsurf/`), Cline (`.clinerules/`)
   - Installs to **all** detected platforms simultaneously — a developer using both VS Code and Claude Code gets both.
3. **Dependency installation** — clones `/clarity` and `/agent-skill-creator` into the primary platform's skill directory, then symlinks to others. No manual setup.
4. **Cross-OS compatibility** — on Windows, falls back from symlinks to directory junctions (no admin required) to copy as a last resort.

A user with git and Python goes from zero to working `/cliskill` in two commands. Dependencies are also auto-installed at runtime via `check_deps.py` if somehow missing after install — defense in depth.

## Architecture

cliskill is a conductor, not an orchestra. It orchestrates two independent skills:

- **`/clarity`** — Reads messy references, produces verified specifications and holdout scenarios
- **`/agent-skill-creator`** — Takes specifications, produces deployed CLI skills on 14+ platforms

Neither skill has an evaluation-fix-rebuild loop. cliskill adds that loop — the piece that turns "generate once and hope" into "generate, verify, fix, verify again."

```
Human provides references
         ↓
    ┌───────────┐
    │ DISCOVER? │  ← If repo + knowledge: extract capabilities, cross-reference,
    └────┬──────┘    rank feasible analytics, user selects
         ↓
    ┌───────────┐     ┌───────────────────────────────────────────────┐
    │ RESEARCH? │─yes─│ NEGOTIATE → BOOTSTRAP → OPTIMIZE → REVIEW    │
    └────┬──────┘     │ (own flow — doesn't enter SPECIFY/BUILD)     │
         │no          └───────────────────────────────────────────────┘
         ↓
    ┌──────────┐
    │ UPDATE?  │  ← If updating: diff new refs against existing spec
    └────┬─────┘
         ↓
    ┌─────────┐
    │ SPECIFY │  ← /clarity (ingest, spec, scenarios, handoff)
    └────┬────┘
         ↓
   [Review Gate 1]  ← Human approves spec (or update plan)
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
    └────┬─────┘         │
         │          needs human?
         │               ↓
         │         ┌───────────┐
         │         │ ESCALATE  │  ← guided, one failure at a time
         │         └─────┬─────┘
         ↓               ↓
      (back to BUILD, max 3 loops)
```

In the standard and discover flows, the human touches the pipeline twice: approving the spec and approving the deployment. In research mode, the human negotiates the metric (NEGOTIATE) and reviews the optimization results (REVIEW). When escalation is needed, cliskill walks the user through each failure interactively — one at a time, with clear options — instead of dumping a diagnostic wall.

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
| **Guided escalation** | No — always ships | Yes — walks user through each failure interactively |
| **Discovery mode** | No — user must know what to build | Yes — cross-references repo capabilities against knowledge sources, ranks feasibility |
| **Research mode** | No — binary pass/fail only | Yes — continuous metric optimization with experiment classification and convergence detection |
| **Update mode** | No — rebuild from scratch | Yes — diffs new refs against existing spec, preserves passing behavior |
| **Self-bootstrapping** | No — user installs deps manually | Yes — produced skills auto-install Python, uv, venv, and deps on first run |
| **Cross-platform** | No — platform-specific build | Yes — every skill ships with bash + PowerShell wrappers |
| **Spec-first workflow** | Optional — can skip to build | Mandatory — /clarity produces verified spec before build |

The critical difference is the last row. agent-skill-creator *can* skip the spec and build directly from raw references. This is fast but fragile — the skill reflects whatever the LLM inferred from the docs, with no structured verification. cliskill forces the spec-first path: clarity extracts, structures, and creates holdout tests *before* the builder ever sees the brief. The builder implements against a verified spec, not against raw inference.

agent-skill-creator remains excellent at what it does — it's the best skill builder available. But it's a build tool, not a factory. cliskill turns it into a factory by adding the quality loop that build tools lack.

Both projects stay independent. agent-skill-creator continues to evolve as the implementation engine. cliskill orchestrates it within a closed-loop pipeline where "it compiled" is no longer sufficient — "it works correctly against scenarios the builder never saw" is the bar.

## Scope and Limitations

**cliskill is good at:**
- APIs with documentation (REST, GraphQL, well-documented libraries)
- Repos with code + reference material (discover mode: cross-reference capabilities against methods)
- PDFs, course materials, textbooks, methodology docs — any structured knowledge source
- Pasted text, URLs, free-text descriptions — anything `/clarity` can ingest
- Continuous metric optimization (research mode: RMSE, Pearson r, F1 — any scalar metric with an eval harness)
- Tools with clear input/output contracts
- Skills that can be expressed as CLI commands with structured JSON output

**cliskill is not designed for:**
- Real-time streaming APIs (WebSockets, SSE) — CLI is request/response
- APIs requiring complex OAuth flows with browser redirects — needs human setup
- Skills that require persistent state across invocations — CLI is stateless by design
- Metrics without deterministic evaluation — if you can't write `metric.py`, research mode can't optimize
- Replacing human judgment on spec review — the review gates exist for a reason

## Metrics That Matter

For a cliskill-produced skill, the quality signals are:

| Metric | What it measures | Typical range |
|---|---|---|
| **Holdout pass rate** | Did the skill pass scenarios the builder never saw? | ~60% on first build → 95%+ after repair loops |
| **Activation precision** | Does the agent reach for this skill at the right time and avoid it at the wrong time? | Measured by trigger/anti-goal coverage in SKILL.md |
| **Context cost** | How many tokens does the agent spend to activate and use the skill? | Target: <500 tokens for activation, vs 50K+ raw API docs |
| **Failure honesty** | When the skill can't help, does the agent say so clearly? | Verified by holdout scenarios that test boundary conditions |
| **Time to first query** | How fast does a new user go from zero to results? | Target: `git clone` + one command. No install step. |

## Links

- **Repository**: [github.com/FrancyJGLisboa/cliskill](https://github.com/FrancyJGLisboa/cliskill)
- **Example skill**: [github.com/FrancyJGLisboa/na-analytics](https://github.com/FrancyJGLisboa/na-analytics) — agricultural commodity analytics, built by cliskill discover mode
- **Dependency — /clarity**: [github.com/FrancyJGLisboa/clarity](https://github.com/FrancyJGLisboa/clarity)
- **Dependency — /agent-skill-creator**: [github.com/FrancyJGLisboa/agent-skill-creator](https://github.com/FrancyJGLisboa/agent-skill-creator)

## License

MIT
