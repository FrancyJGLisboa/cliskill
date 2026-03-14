# cliskill — AI-Agent-Friendly CLI Skill Framework

> Your agents don't need to read the docs. They need a tool that already did.

![cliskill — Self-Bootstrapping CLI Skills for AI Agents](cliskill.png)

cliskill turns any reference material — API docs, repositories, PDFs, course materials, pasted text — into **self-bootstrapping CLI tools** that AI agents fully understand and users just clone and run. It delegates specification to [/clarity](https://github.com/FrancyJGLisboa/clarity), implementation to [/agent-skill-creator](https://github.com/FrancyJGLisboa/agent-skill-creator), and adds what neither has: an **automated evaluation-fix-rebuild loop**.

## What This Is

A framework for generating self-installing, cross-platform, agent-friendly CLI skills from any reference material. The produced skills are git repos that work on any OS (`./skill` on macOS/Linux, `.\skill.ps1` on Windows) and any agent tool (Claude Code, Copilot, Cursor, Windsurf, Gemini CLI, Codex, Goose, OpenCode, Cline).

```
API References → SPECIFY → [Review] → BUILD → VERIFY → DEPLOY
                                         ↑        ↓
                                         ← REPAIR ←
```

The human provides references and reviews twice. Everything between is autonomous.

## Install

**macOS / Linux:**

```bash
git clone https://github.com/FrancyJGLisboa/cliskill
cd cliskill
./cliskill
```

**Windows (PowerShell):**

```powershell
git clone https://github.com/FrancyJGLisboa/cliskill
cd cliskill
.\cliskill.ps1
```

That's it. The installer:

1. Checks prerequisites (git, Python 3.10+) with OS-specific install guidance if missing
2. Detects your AI coding tool (Claude Code, Cursor, Copilot, Windsurf, Gemini CLI, Codex, Goose, OpenCode, Cline)
3. Installs cliskill **and both dependencies** (`/clarity`, `/agent-skill-creator`) automatically
4. On Windows, falls back to directory junctions or copy if symlinks need admin

Other options:

```bash
./cliskill --dry-run      # Preview without changes
./cliskill --uninstall    # Remove symlinks
```

### Dependencies

cliskill depends on two skills — both are **auto-installed** by `--with-deps`:

- **[/clarity](https://github.com/FrancyJGLisboa/clarity)** — Specification engine
- **[/agent-skill-creator](https://github.com/FrancyJGLisboa/agent-skill-creator)** — Implementation engine

If you skip `--with-deps`, dependencies are still auto-installed at runtime when you first run `/cliskill`.

To verify manually:

```bash
python3 scripts/check_deps.py      # macOS/Linux
python scripts/check_deps.py       # Windows
```

## Usage

### Create a new skill

```
/cliskill <reference-1> [<reference-2> ...]
```

References can be: API documentation, repository URLs, file paths, PDFs, URLs, or free-text descriptions.

**Examples:**

```
/cliskill https://api.example.com/docs https://github.com/example/weather-api
/cliskill ./specs/finnhub-api-reference.pdf
/cliskill https://developers.notion.com/reference "bidirectional sync to markdown"
```

### Update an existing skill

When the API changes — new endpoints, breaking changes, deprecated features — update instead of starting from scratch:

```
/cliskill update <existing-skill-path> <new-reference-1> [...]
```

**Examples:**

```
/cliskill update ./weather-api-skill https://api.example.com/docs/v2
/cliskill update ./notion-sync-skill https://developers.notion.com/reference/changelog
```

Update mode diffs the new references against the existing spec, shows you what changed, and only re-specs the delta. Existing passing scenarios are preserved and re-run to catch regressions.

### Discover what's possible (repo + knowledge)

When you have a repo and want to find out what it can do — cross-referenced against course materials, textbooks, or methodology docs:

```
/cliskill discover <capability-refs> [-- <knowledge-refs>]
```

**Examples:**

```
/cliskill discover https://github.com/john/portfolio-repo -- ./quant-finance-course.pdf
/cliskill discover ./my-data-pipeline -- ./analytics-textbook.pdf "focus on risk analytics"
```

Discovery mode analyzes the repo's data structures, functions, and libraries, extracts methods from the knowledge material, cross-references them to find what's feasible, and ranks by importance × effort. You pick which analytics to include, then the standard pipeline builds and verifies the skill.

### Research mode (continuous optimization)

When you have a model or pipeline and want to optimize a continuous metric (RMSE, Pearson r, F1) rather than hit binary pass/fail:

```
/cliskill research <capability-refs> [-- <knowledge-refs>]
```

**Examples:**

```
/cliskill research ./my-ml-pipeline -- ./methodology-paper.pdf "optimize RMSE for yield prediction"
/cliskill research https://github.com/user/forecasting-repo -- ./domain-guide.pdf
```

Research mode combines discovery (what can this code do?) with metric negotiation (what does "better" mean?) and runs an autonomous optimization loop — proposing changes, evaluating them, classifying failures, and keeping or reverting. It brings cliskill's rigor (failure classification, convergence detection, guided escalation) to the autoresearch pattern of continuous improvement.

### Resume an interrupted pipeline

```
/cliskill resume
```

## How It Works

### Phase 1: SPECIFY

Delegates to `/clarity` (INGEST → SPECIFY → SCENARIO → HANDOFF). Produces a structured spec, holdout scenarios, and a skill brief.

**Review Gate:** You review and approve the spec before building.

### Phase 2: BUILD

Delegates to `/agent-skill-creator`. Passes the skill brief — agent-skill-creator skips its Discovery and Design phases since the brief already covers those decisions.

### Phase 3: VERIFY

Delegates to `/clarity evaluate`. Runs the built skill against holdout scenarios. If all pass, proceed to deploy. If any fail, enter the repair loop.

### The Evaluation Loop

The core innovation. When verification fails, cliskill classifies each failure:

| Root Cause | Action |
|---|---|
| **Spec Gap** | Update spec, regenerate brief, rebuild |
| **Implementation Gap** | Generate targeted fix prompt, rebuild |
| **Scenario Gap** | Guided escalation — you decide, not cliskill |

Rules:
- **3 loops maximum.** If not converged, escalate with guided resolution.
- **Fix spec first.** Spec fixes often resolve implementation gaps as a side effect.
- **Never auto-fix tests.** If the holdout test is wrong, only a human should change it.
- **Preserve passing behavior.** Rebuilds target only failing scenarios.

### Guided Escalation

When cliskill needs your input (scenario gaps, convergence failures, loop exhaustion), it doesn't dump a wall of diagnostics. Instead, it walks you through each failure one at a time:

- Shows what it expected vs. what happened
- Gives its best-guess classification with reasoning
- Offers clear options: agree, reclassify, fix the test, see the code, or skip
- Summarizes the plan before executing

### Discovery Mode

When you don't know what the skill should do — you have a repo and reference material (course PDFs, textbooks) — discovery mode figures it out:

1. **Extracts capabilities** from the repo (data, functions, libraries, pipelines)
2. **Extracts methods** from the knowledge material (techniques, prerequisites, importance)
3. **Cross-references** to find what's feasible and what's blocked
4. **Ranks** by importance × effort into tiers (quick wins, worth building, stretch goals)
5. **You select** which analytics to include, then the pipeline builds and verifies

### Research Mode

When you need continuous optimization rather than binary pass/fail, research mode runs the autoresearch loop with cliskill's rigor:

1. **DISCOVER** — inventory capabilities, extract methods from knowledge sources
2. **NEGOTIATE** — define what "better" means via a metric-compiler conversation
3. **BOOTSTRAP** — generate the optimization harness, verify the metric against known cases
4. **OPTIMIZE** — PROPOSE → RUN → CLASSIFY → KEEP/REVERT, with experiment classification (implementation bug, destructive hypothesis, exhausted direction, neutral result) and strategy class tracking
5. **REVIEW** — present Pareto front and strategy summary; human accepts, refines metric, or continues

The loop runs until convergence stalls across multiple strategy classes, then escalates with guided review.

### Update Mode

When the API changes, `cliskill update` avoids starting from scratch. It diffs the new references against the existing spec, shows you what's new/changed/deprecated, and only re-specs the delta. All existing scenarios are re-run to catch regressions.

### Phase 4: DEPLOY

**Review Gate:** You approve deployment after all scenarios pass.

Installs the skill to all detected platforms.

## What Makes the Output "Agent-Friendly"

The CLI skills produced by cliskill aren't just wrappers. They are self-contained, self-installing git repositories:

- **Clone and run** — `./skill <command>` auto-bootstraps Python, uv, venv, and dependencies on first run. No manual setup.
- **Cross-platform** — bash wrapper (`./skill`) + PowerShell wrapper (`.\skill.ps1`). Works on macOS, Linux, and Windows.
- **JSON output** — structured JSON to stdout for agent consumption. Errors as JSON to stderr with exit code 1.
- **SKILL.md** with clear trigger descriptions — agents know *when* to reach for this tool
- **Anti-goals** — agents know what *not* to attempt
- **Error handling guidance** — agents know how to fail gracefully and what to tell the user
- **Holdout-verified behavior** — the skill was tested against scenarios the builder never saw
- **Activation keywords** — agents can match user intent to the right skill
- **Works on any agent tool** — pure CLI interface means Claude Code, Copilot, Cursor, Windsurf, Gemini CLI, Codex, Goose, OpenCode, and Cline can all execute it

### Example

[na-analytics](https://github.com/FrancyJGLisboa/na-analytics) — built by cliskill from a commodity price ETL repo + a trading course PDF:

```bash
$ git clone https://github.com/FrancyJGLisboa/na-analytics && cd na-analytics
$ ./na-analytics ppe --commodity soja
# auto-installs deps, fetches live data from GitHub, returns:
{"results": {"exw_brl_sc": 140.70}, "resolved_from_pipeline": {"cbot": 1218.25, "fx": 5.3535}}
```

11 commands, zero setup, live data, verified against course formulas.

## Platform Support

**User-level** (global — available across all projects):

| Platform | Detection | Install path |
|----------|-----------|-------------|
| Claude Code | `~/.claude/` | `~/.claude/skills/` |
| VS Code + Copilot | `~/.copilot/` or `code` in PATH | `~/.copilot/skills/` |
| Cursor | `~/.cursor/` | `~/.cursor/rules/` |
| Windsurf | `~/.codeium/windsurf/` | `~/.windsurf/rules/` |
| Gemini CLI | `~/.gemini/` | `~/.gemini/skills/` |
| Codex CLI | `~/.codex/` | `~/.codex/skills/` |
| Goose | `~/.config/goose/` | `~/.config/goose/skills/` |
| OpenCode | `~/.config/opencode/` | `~/.config/opencode/skills/` |

**Project-level** (scoped to current repo):

| Platform | Detection | Install path |
|----------|-----------|-------------|
| GitHub Copilot | `.github/` in project | `.github/skills/` |
| Cursor | `.cursor/` in project | `.cursor/rules/` |
| Windsurf | `.windsurf/` in project | `.windsurf/rules/` |
| Cline | `.clinerules/` in project | `.clinerules/` |

If no platform is detected, defaults to Claude Code. The installer installs to **all** detected platforms simultaneously.

## Architecture

```
cliskill/
├── cliskill                        # Self-bootstrapping installer (macOS/Linux)
├── cliskill.ps1                    # Self-bootstrapping installer (Windows)
├── SKILL.md                        # The pipeline specification
├── references/
│   ├── discovery-protocol.md       # Capability extraction + feasibility
│   ├── evaluation-router.md        # Failure classification + routing
│   ├── loop-protocol.md            # State tracking + convergence rules
│   ├── research-protocol.md        # Continuous optimization loops
│   └── examples.md                 # Happy path + fix loop examples
├── scripts/
│   ├── check_deps.py               # Dependency checker + auto-installer
│   ├── install.sh                  # Shell installer (macOS/Linux)
│   └── install.ps1                 # PowerShell installer (Windows)
├── APPLICATION_CARD.md
├── README.md
└── LICENSE
```

Runtime artifacts (created during a cliskill run):

```
.cliskill/                          # Pipeline state + loop history
.clarity/                           # Spec, context, skill brief, evaluations
scenarios/                          # Holdout scenarios
{skill-name}/                       # The built skill
```

## License

MIT — see [LICENSE](LICENSE).
