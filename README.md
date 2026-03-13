# cliskill — AI-Agent-Friendly CLI Skill Framework

> Point at API references. Get a verified CLI tool that agents know how to wield.

cliskill turns API references into production-ready CLI tools that AI agents fully understand — how to use them, when to use them, when not to, and when to honestly give up. It delegates specification to [/clarity](https://github.com/FrancyJGLisboa/clarity), implementation to [/agent-skill-creator](https://github.com/FrancyJGLisboa/agent-skill-creator), and adds what neither has: an **automated evaluation-fix-rebuild loop**.

## What This Is

A framework for building agent-native CLI skills. Not just CLI wrappers around APIs — skills that an AI agent can read, understand its limits, and wield with judgment.

```
API References → SPECIFY → [Review] → BUILD → VERIFY → DEPLOY
                                         ↑        ↓
                                         ← REPAIR ←
```

The human provides references and reviews twice. Everything between is autonomous.

## Prerequisites

Both skills must be installed:

- **[/clarity](https://github.com/FrancyJGLisboa/clarity)** — Specification engine
- **[/agent-skill-creator](https://github.com/FrancyJGLisboa/agent-skill-creator)** — Implementation engine

## Install

### One-liner (any platform with npm)

```bash
npx skills add FrancyJGLisboa/cliskill -g
```

The `-g` flag installs globally (available across all projects). cliskill is a meta-tool that builds other skills — it should always be global, not scoped to a single repo.

### macOS / Linux

```bash
git clone https://github.com/FrancyJGLisboa/cliskill
cd cliskill
./scripts/install.sh
```

To also install missing dependencies:

```bash
./scripts/install.sh --with-deps
```

Other options:

```bash
./scripts/install.sh --dry-run      # Preview without changes
./scripts/install.sh --uninstall    # Remove symlinks
```

### Windows (PowerShell)

```powershell
git clone https://github.com/FrancyJGLisboa/cliskill
cd cliskill
.\scripts\install.ps1
```

With dependencies:

```powershell
.\scripts\install.ps1 -WithDeps
```

Other options:

```powershell
.\scripts\install.ps1 -DryRun      # Preview without changes
.\scripts\install.ps1 -Uninstall   # Remove symlinks/junctions
```

> **Note:** On Windows, symlinks require Developer Mode or admin privileges. The installer falls back to directory junctions (no admin needed), then to copy as a last resort.

### Verify dependencies

```bash
python3 scripts/check_deps.py      # macOS/Linux
python scripts/check_deps.py       # Windows
```

## Usage

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

Resume an interrupted pipeline:

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
| **Scenario Gap** | Escalate to human (holdout tests are sacred) |

Rules:
- **3 loops maximum.** If not converged, escalate with diagnostics.
- **Fix spec first.** Spec fixes often resolve implementation gaps as a side effect.
- **Never auto-fix tests.** If the holdout test is wrong, only a human should change it.
- **Preserve passing behavior.** Rebuilds target only failing scenarios.

### Phase 4: DEPLOY

**Review Gate:** You approve deployment after all scenarios pass.

Installs the skill to all detected platforms.

## What Makes the Output "Agent-Friendly"

The CLI skills produced by cliskill aren't just API wrappers. They include:

- **SKILL.md** with clear trigger descriptions — agents know *when* to reach for this tool
- **Anti-goals** — agents know what *not* to attempt
- **Error handling guidance** — agents know how to fail gracefully and what to tell the user
- **Holdout-verified behavior** — the skill was tested against scenarios the builder never saw
- **Activation keywords** — agents can match user intent to the right skill

## Platform Support

| Platform | Detection |
|----------|-----------|
| Claude Code | `~/.claude` |
| GitHub Copilot | `~/.copilot` |
| Gemini CLI | `~/.gemini` |
| Codex CLI | `~/.agents` |
| Goose | `~/.config/goose` |
| OpenCode | `~/.config/opencode` |

## Architecture

```
cliskill/
├── SKILL.md                        # The pipeline specification
├── references/
│   ├── evaluation-router.md        # Failure classification + routing
│   ├── loop-protocol.md            # State tracking + convergence rules
│   └── examples.md                 # Happy path + fix loop examples
├── scripts/
│   ├── check_deps.py               # Dependency checker
│   ├── install.sh                  # Installer (macOS/Linux)
│   └── install.ps1                 # Installer (Windows PowerShell)
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
