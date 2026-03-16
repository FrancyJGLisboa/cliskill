---
name: cliskill
description: >-
  Generates self-bootstrapping, cross-platform, agent-friendly CLI skills from
  any reference material — API docs, repositories, PDFs, course materials,
  pasted text, URLs. Produced skills are git repos: clone and run on any OS,
  any agent tool. Closed-loop pipeline: specify, build, evaluate, auto-fix,
  rebuild. Uses /clarity for specification and holdout verification,
  /agent-skill-creator for implementation and deployment.
  Triggers on: cliskill, build cli skill, agent-friendly cli, api to cli skill,
  end-to-end skill pipeline, create and verify skill, update existing skill,
  api changed update skill, discover what analytics are possible, turn repo
  into agent skill, cross-reference repo with course material, turn PDF into
  CLI tool, build skill from documentation, optimize model metrics, continuous
  optimization loop, research mode, autoresearch with cliskill.
license: MIT
metadata:
  author: Francy Lisboa Charuto
  version: 1.0.0
  created: 2026-03-13
  last_reviewed: 2026-03-13
  review_interval_days: 90
  scope: global
---

# cliskill — AI-Agent-Friendly CLI Skill Framework

> Point at any reference material. Get a self-installing CLI tool that agents know how to wield.

cliskill is a closed-loop pipeline that transforms any reference material — API docs, repositories, PDFs, course materials, pasted text — into **self-bootstrapping CLI skills** that work on any OS and any agent tool. The produced skills are git repos: users clone and run, agents read the SKILL.md and wield. It delegates specification to `/clarity`, implementation to `/agent-skill-creator`, and adds what neither has: an **automated evaluation-fix-rebuild loop** and **self-bootstrapping packaging**.

The human provides references and reviews twice. Everything else is autonomous.

## Trigger

```
/cliskill <reference-1> [<reference-2> ...]
/cliskill resume
/cliskill update <existing-skill-path> <new-reference-1> [<new-reference-2> ...]
/cliskill discover <capability-ref-1> [<capability-ref-2> ...] -- <knowledge-ref-1> [<knowledge-ref-2> ...]
/cliskill research <capability-ref-1> [<capability-ref-2> ...] -- <knowledge-ref-1> [<knowledge-ref-2> ...]
/cliskill self-improve
```

References can be: API documentation, repository URLs, file paths, PDFs, URLs, or free-text descriptions — anything `/clarity` can ingest.

**Examples:**
```
/cliskill https://api.example.com/docs https://github.com/example/weather-api
/cliskill ./specs/finnhub-api-reference.pdf
/cliskill resume
/cliskill update ./weather-api-skill https://api.example.com/docs/v2
/cliskill discover https://github.com/john/portfolio-repo -- ./course-materials/quantitative-finance.pdf
/cliskill discover ./my-data-pipeline -- ./analytics-textbook.pdf "focus on risk analytics"
/cliskill research ./my-ml-pipeline -- ./methodology-paper.pdf "optimize RMSE for yield prediction"
```

**Natural language works too.** Users don't need to know the subcommands. cliskill infers the right mode from intent:
```
/cliskill ./my-repo ./finance-textbook.pdf "what analytics can I build?"    → detects DISCOVER
/cliskill ./my-pipeline ./methods-paper.pdf "make predictions better"       → detects RESEARCH
/cliskill https://api.stripe.com/docs "wrap this API"                       → detects STANDARD
```
See "Phase Detection — Step 2: Intent Inference" for classification rules. When the mode is ambiguous, cliskill confirms before proceeding.

The `--` separator in discover mode separates capability sources (repos, code, data) from knowledge sources (courses, textbooks, methodology docs). If omitted, the agent classifies each reference automatically.

## Core Principles

1. **Zero friction by default.** When the intent is unambiguous, the pipeline runs end-to-end without any human interaction. The vibe contract is generated and verified internally — the human only sees it if something goes wrong. When the intent is ambiguous, the human approves 3–5 binary checks (one touchpoint). Review gates auto-approve when the vibe contract is satisfied.
2. **Holdout scenarios are sacred. This is a hard constraint, not a guideline.** Never auto-fix a failing holdout test. Never weaken a scenario to make it pass. If the test is wrong, that's a Scenario Gap — escalate to the human. If cliskill ever auto-patches holdout scenarios, the entire verification primitive collapses.
3. **Three loops maximum.** If the evaluation-fix cycle hasn't converged in 3 iterations, escalate with full diagnostics. Don't spin.
4. **Fix spec first.** When both spec and implementation gaps exist, fix the spec first — implementation gaps often self-resolve when the spec is corrected.
5. **Preserve passing behavior.** Rebuilds target only failing scenarios. Never re-architect what already works.
6. **State is resumable.** Every phase writes state to `.cliskill/`. If interrupted, `/cliskill resume` picks up where it left off.
7. **Agent-native output.** The produced CLI skill must be fully understandable by AI agents — clear activation triggers, explicit limitations, honest failure modes, and well-defined anti-goals.
8. **Show progress, don't go silent.** Emit a status line at every phase and sub-phase boundary so the user always knows what's happening.

## Progress Reporting

The pipeline can run for minutes between review gates. Emit a structured status line at every phase boundary, sub-phase transition, and significant event. Never let more than ~30 seconds of visible work pass without a status update.

### Format

```
cliskill ▸ {PHASE} ▸ {sub-phase}  {detail}
```

### Required Status Lines

Emit these at the indicated points — they are not optional:

**VIBE phase (silent path):**
```
cliskill ▸ VIBE ▸ starting       Analyzing request...
cliskill ▸ VIBE ▸ checks         {N} checks generated (auto-approved — intent clear)
cliskill ▸ VIBE ▸ done           Proceeding autonomously
```

**VIBE phase (interactive path):**
```
cliskill ▸ VIBE ▸ starting       Analyzing request...
cliskill ▸ VIBE ▸ checks         {N} checks generated — need your input
cliskill ▸ VIBE ▸ approved       {N}/{N} checks approved — vibe contract locked
cliskill ▸ VIBE ▸ done           Proceeding autonomously
```

**DETECT (intent inference):**
```
cliskill ▸ DETECT ▸ intent       Analyzing references and request...
cliskill ▸ DETECT ▸ intent       Detected: {DISCOVER | RESEARCH | STANDARD} mode
cliskill ▸ DETECT ▸ confirmed    User confirmed: {mode}
```

**DISCOVER mode (when applicable):**
```
cliskill ▸ DISCOVER ▸ starting     Analyzing {N} capability + {N} knowledge source(s)
cliskill ▸ DISCOVER ▸ classify     {reference}: {capability | knowledge | both}
cliskill ▸ DISCOVER ▸ capabilities Reading {source name}...
cliskill ▸ DISCOVER ▸ capabilities {N} data structures, {N} functions, {N} pipelines found
cliskill ▸ DISCOVER ▸ capabilities {N} unverified (excluded from ranking)
cliskill ▸ DISCOVER ▸ knowledge    Reading {source name}...
cliskill ▸ DISCOVER ▸ knowledge    {N} methods extracted ({M} high-confidence, {K} low-confidence)
cliskill ▸ DISCOVER ▸ crossref     Matching capabilities against methods...
cliskill ▸ DISCOVER ▸ crossref     {N} feasible, {N} blocked
cliskill ▸ DISCOVER ▸ probes       Running feasibility probes on {N} candidates...
cliskill ▸ DISCOVER ▸ probes       {N} passed, {M} downgraded, {K} blocked
cliskill ▸ DISCOVER ▸ ranking      Scoring and ranking (post-probe)...
cliskill ▸ DISCOVER ▸ done         Discovery complete — {N} Tier 1, {N} Tier 2, {N} Tier 3, {N} blocked
```

**SPECIFY phase:**
```
cliskill ▸ SPECIFY ▸ starting    Delegating to /clarity with {N} reference(s)
cliskill ▸ SPECIFY ▸ INGEST      Reading {reference name/URL}...
cliskill ▸ SPECIFY ▸ INGEST      {N} endpoints / {N} models extracted
cliskill ▸ SPECIFY ▸ SPECIFY     Generating spec...
cliskill ▸ SPECIFY ▸ SPECIFY     {N} requirements drafted
cliskill ▸ SPECIFY ▸ SCENARIO    Creating holdout scenarios...
cliskill ▸ SPECIFY ▸ SCENARIO    {N} scenarios created
cliskill ▸ SPECIFY ▸ HANDOFF     Generating skill brief...
cliskill ▸ SPECIFY ▸ done        Ready for review — {N} requirements, {N} scenarios
```

**BUILD phase:**
```
cliskill ▸ BUILD ▸ starting      Delegating to /agent-skill-creator
cliskill ▸ BUILD ▸ architecture  Designing skill structure...
cliskill ▸ BUILD ▸ detection     Detecting target platforms...
cliskill ▸ BUILD ▸ detection     Found: {platform list}
cliskill ▸ BUILD ▸ implement     Building {skill-name}...
cliskill ▸ BUILD ▸ validate      Running validation + security scan...
cliskill ▸ BUILD ▸ done          {skill-name} built ({N} files)
```

**VERIFY phase:**
```
cliskill ▸ VERIFY ▸ starting     Running {N} holdout scenarios...
cliskill ▸ VERIFY ▸ SC-{NNN}     ✓ {scenario title}
cliskill ▸ VERIFY ▸ SC-{NNN}     ✗ {scenario title} — {root cause hint}
cliskill ▸ VERIFY ▸ done         {passed}/{total} passed
```

**REPAIR LOOP:**
```
cliskill ▸ REPAIR ▸ loop {N}     {M} failure(s) to fix
cliskill ▸ REPAIR ▸ classify     SC-{NNN}: {Spec Gap | Implementation Gap | Scenario Gap}
cliskill ▸ REPAIR ▸ fix-spec     Updating {N} requirement(s) in spec...
cliskill ▸ REPAIR ▸ fix-impl     Generating rebuild context for {N} failure(s)...
cliskill ▸ REPAIR ▸ rebuilding   Back to BUILD (loop {N} of 3)
```

**DEPLOY phase:**
```
cliskill ▸ DEPLOY ▸ starting     Installing to {N} platform(s)...
cliskill ▸ DEPLOY ▸ installed    {platform-name} ✓
cliskill ▸ DEPLOY ▸ done         Deployed to {platform list}
```

**SELF-IMPROVE mode:**
```
cliskill ▸ SELF-IMPROVE ▸ starting     Loading build history ({N} builds)
cliskill ▸ SELF-IMPROVE ▸ metrics      first_pass_rate: {v}, avg_loops: {v}, escalation_rate: {v}
cliskill ▸ SELF-IMPROVE ▸ metrics      Weakest: {metric name} ({value})
cliskill ▸ SELF-IMPROVE ▸ experiment   Active experiment E-{NNN}: {status}
cliskill ▸ SELF-IMPROVE ▸ hypothesis   Target: {file} — {hypothesis summary}
cliskill ▸ SELF-IMPROVE ▸ review       Presenting proposed change for approval...
cliskill ▸ SELF-IMPROVE ▸ applied      Change committed: {sha}
cliskill ▸ SELF-IMPROVE ▸ classify     E-{NNN}: {KEEP | REVERT | INCONCLUSIVE} — {metric}: {before} → {after}
cliskill ▸ SELF-IMPROVE ▸ done         {summary}
```

**RESEARCH mode (when applicable):**
```
cliskill ▸ RESEARCH ▸ starting    Research mode — continuous optimization
cliskill ▸ RESEARCH ▸ discover    Running discovery pipeline...
cliskill ▸ RESEARCH ▸ discover    {N} capabilities, {N} methods found
cliskill ▸ RESEARCH ▸ negotiate   Asking scenario questions...
cliskill ▸ RESEARCH ▸ negotiate   Metric proposed: {metric name}
cliskill ▸ RESEARCH ▸ negotiate   Metric accepted: {metric name}
cliskill ▸ RESEARCH ▸ bootstrap   Generating eval harness...
cliskill ▸ RESEARCH ▸ bootstrap   Dry-run: {N} experiments passed
cliskill ▸ RESEARCH ▸ bootstrap   Metric verified against known cases
cliskill ▸ RESEARCH ▸ optimize    Experiment {N}: {strategy class} — {hypothesis}
cliskill ▸ RESEARCH ▸ optimize    Experiment {N}: {KEEP | REVERT | BUG | DESTRUCTIVE} — {metric} → {new metric}
cliskill ▸ RESEARCH ▸ optimize    Strategy class {name} exhausted ({N} neutral in a row)
cliskill ▸ RESEARCH ▸ optimize    Convergence stalled — {N} classes exhausted
cliskill ▸ RESEARCH ▸ review      Presenting results — best: {metric value}, {N} experiments, {M} kept
cliskill ▸ RESEARCH ▸ done        Research complete — {metric}: {baseline} → {best}
```

### Rules

- **Every status line is a single line.** No multi-line updates — these should scroll cleanly in a terminal.
- **Include counts when available.** "{N} requirements" is better than "requirements generated."
- **Name things.** "Reading finnhub-api-reference.pdf" is better than "Reading reference..."
- **On resume**, emit a catchup line: `cliskill ▸ RESUME ▸ {phase}  Resuming from {phase}, loop {N}`
- **On escalation**, the escalation block (defined in loop-protocol.md) replaces the status line — don't emit a status line AND an escalation block.

## Reference Files

Load these on demand when entering the relevant phase:

| File | Load when |
|------|-----------|
| `references/discovery-protocol.md` | Entering DISCOVER mode |
| `references/evaluation-router.md` | Entering VERIFY phase or REPAIR LOOP |
| `references/loop-protocol.md` | Entering REPAIR LOOP or processing `/cliskill resume` |
| `references/research-protocol.md` | Entering RESEARCH mode |
| `references/examples.md` | When needing pattern reference for any phase |
| `references/self-improvement-protocol.md` | Entering SELF-IMPROVE mode, or at end of any pipeline run (DEPLOY / terminal escalation) |

## Dependencies

cliskill orchestrates two existing skills:

- **`/clarity`** — Specification engine (INGEST → SPECIFY → SCENARIO → HANDOFF → EVALUATE)
- **`/agent-skill-creator`** — Implementation engine (Discovery → Design → Architecture → Detection → Implementation)

**Before starting any pipeline run**, check dependencies by running `python3 scripts/check_deps.py`. The script will:

1. **Detect the user's platform** (Claude Code, Cursor, Copilot, Windsurf, Cline, Codex, Gemini, Goose, OpenCode)
2. **Check if both skills are installed** in the detected platform's skill directory
3. **Auto-install any missing dependency** via `git clone --depth 1` to the appropriate location
4. If auto-install fails (no git, no network, no platform detected), print manual install instructions

This means a fresh user running `/cliskill` for the first time gets dependencies installed automatically — no manual setup required.

## Invocation Model

cliskill invokes sub-skills **inline** — the orchestrating agent reads the sub-skill's SKILL.md and follows its instructions within the current context. There are no subprocess calls or separate agent contexts.

**Context window implications:** A full pipeline accumulates clarity's work + agent-skill-creator's work + repair loop artifacts. To manage this:

1. **Phase boundaries are context boundaries.** After each phase completes, its detailed working state lives on disk (`.clarity/`, `.cliskill/`), not in context. The agent should summarize phase results and release intermediate reasoning.
2. **Sub-skill reference files are loaded on demand.** Don't load clarity's full reference library at the start — load what each phase needs, then release it.
3. **Rebuild loops carry only the delta.** On re-BUILD, pass the skill brief + rebuild context, not the full evaluation history. Previous loop artifacts are on disk for diagnostics, not in context for the builder.
4. **If context pressure forces a restart,** `.cliskill/state.md` + disk artifacts are sufficient to resume. The agent does not need to reconstruct the full conversation history.

This model means cliskill works best with agents that have large context windows (100K+). For complex skills that generate large specs, the pipeline may require `/cliskill resume` at phase boundaries if context fills up.

---

## Phase Detection & Resume

On every invocation, first try explicit command matching, then intent inference.

### Step 1: Explicit Command Matching

```
if command is "/cliskill discover <refs> [-- <knowledge-refs>]":
    → enter DISCOVER mode (see Phase D: DISCOVER below)

else if command is "/cliskill research <refs> [-- <knowledge-refs>]":
    → enter RESEARCH mode (see Phase R: RESEARCH below)

else if command is "/cliskill update <skill-path> <refs>":
    → enter UPDATE mode (see Phase 0: UPDATE below)

else if command is "/cliskill self-improve":
    → enter SELF-IMPROVE mode (see Phase S: SELF-IMPROVE below)

else if .cliskill/state.md exists AND command is "/cliskill resume":
    read state.md → determine current phase and loop count
    resume from recorded phase
else if .cliskill/state.md exists AND command is "/cliskill <refs>":
    warn: "Found existing .cliskill/ state. Resume with /cliskill resume or delete .cliskill/ to start fresh."
    stop
else:
    → go to Step 2: Intent Inference
```

### Step 2: Intent Inference

Most users — especially vibe coders — won't type `/cliskill discover` or `/cliskill research`. They'll say things like "I have this repo and a finance textbook, make me something useful" or "optimize my prediction pipeline." The agent must detect the right mode from intent, not syntax.

**Run this classification before defaulting to standard SPECIFY:**

```
Analyze the user's request + references. Classify intent:

SIGNAL → DISCOVER mode:
  - Multiple reference types (repo + PDF, code + course material, data + textbook)
  - Vague or open-ended goal ("what can I do with this", "find useful analytics",
    "build me something from these", "what's possible")
  - User doesn't specify what the skill should do — they want cliskill to figure it out
  - Knowledge source present (course material, textbook, methodology doc)
    without a clear mapping to a specific skill

SIGNAL → RESEARCH mode:
  - Continuous metric mentioned or implied ("optimize", "improve", "better predictions",
    "reduce error", "increase accuracy", "tune", "maximize", "minimize")
  - Existing pipeline/model that works but could be better
  - User wants to iterate, not just build once
  - References include methodology/technique docs for improving something that exists

SIGNAL → STANDARD mode:
  - Clear, specific goal ("wrap this API", "turn these docs into a CLI tool")
  - API documentation as primary reference
  - User knows exactly what the skill should do
  - References are specifications, not exploratory material

If classified as DISCOVER or RESEARCH, confirm with the user before proceeding:
```

```
cliskill ▸ DETECT ▸ intent    Analyzing references and request...
cliskill ▸ DETECT ▸ intent    Detected: {DISCOVER | RESEARCH} mode
```

```
## cliskill — Mode Detection

Based on your request, this looks like a **{discover | research}** scenario:

{1-2 sentence explanation of why}

**Options:**
1. **{Discover | Research} mode** — {brief description of what will happen}
2. **Standard mode** — skip discovery, go straight to SPECIFY (you already know what to build)
3. **Tell me more** — explain the difference
```

Wait for user response before proceeding.

**Why confirm:** Mode inference can be wrong. A false positive (sending a clear API-wrapping task through DISCOVER) wastes time. A false negative (sending a vague exploratory task through SPECIFY) produces a bad spec. The confirmation is cheap — one question — and prevents costly misrouting.

**Do NOT confirm if the intent is clearly standard.** If the user provides API docs and says "build a CLI for this," skip inference and go to SPECIFY. The confirmation is only for ambiguous cases where DISCOVER or RESEARCH signals are present.

### Step 3: VIBE Phase

After mode is determined (by explicit command or intent inference), **always run Phase V: VIBE first** — unless:
- Command is `/cliskill resume` (reload existing vibe contract from `.cliskill/vibe-contract.md`)
- Command is `/cliskill self-improve` (no skill being built, no vibe needed)

VIBE produces the vibe contract, then the pipeline continues into the detected mode (DISCOVER → SPECIFY → BUILD → VERIFY → DEPLOY, etc.). All downstream review gates check against the vibe contract for auto-approval.

---

## Phase D: DISCOVER (conditional)

**Entry:** `/cliskill discover <capability-refs> [-- <knowledge-refs>]`

**Load:** `references/discovery-protocol.md`

Discovery mode handles the case where the user doesn't know exactly what the skill should do — they have sources of capability (a repo, a library, data) and sources of knowledge (course materials, textbooks) and want to find what's possible at the intersection.

### Instructions

1. **Classify references.** If the user used `--` separator, references before it are capability sources and after are knowledge sources. If no separator, classify each reference:
   - Repos, code files, data schemas, APIs → **capability source**
   - PDFs, course materials, textbooks, methodology docs → **knowledge source**
   - Mixed (e.g., repo with tutorial notebooks) → **both**

2. **Phase D1 — Capability Extraction.** Analyze each capability source. For repos, use reverse-engineering to extract data structures, functions, data sources, existing pipelines, and library capabilities. **Guardrail G1.1: every claim must cite file:line as evidence.** Unverified capabilities go in a separate section (G1.3). Write to `.cliskill/discovery/capabilities.md`.

```
cliskill ▸ DISCOVER ▸ capabilities Reading {source name}...
cliskill ▸ DISCOVER ▸ capabilities {N} data structures, {N} functions, {N} pipelines found
```

3. **Phase D2 — Knowledge Extraction.** Analyze each knowledge source. Extract methods/techniques with their prerequisites, outputs, complexity, and importance. **Guardrail G1.5: only include methods the source explicitly teaches (with formulas/examples), not methods the agent infers.** Write to `.cliskill/discovery/knowledge.md`.

```
cliskill ▸ DISCOVER ▸ knowledge    Reading {source name}...
cliskill ▸ DISCOVER ▸ knowledge    {N} methods/techniques extracted
```

4. **Phase D3 — Cross-Reference + Probes.** Match capabilities against knowledge methods. For each method, assess data readiness and function readiness. **Then run feasibility probes on every READY/LOW_EFFORT candidate (G1.2).** Probes verify claims by reading actual code — failed probes downgrade the classification. Validate full prerequisite chains (G1.4). Write to `.cliskill/discovery/cross-reference.md` and `.cliskill/discovery/probes.md`.

```
cliskill ▸ DISCOVER ▸ crossref     Matching capabilities against methods...
cliskill ▸ DISCOVER ▸ crossref     {N} feasible, {N} blocked
cliskill ▸ DISCOVER ▸ probes       Running feasibility probes on {N} candidates...
cliskill ▸ DISCOVER ▸ probes       {N} passed, {M} downgraded, {K} blocked
```

5. **Phase D4 — Ranking.** Rank feasible methods (post-probe) by importance × feasibility. Group into tiers (Tier 1: quick wins, Tier 2: worth building, Tier 3: stretch goals, Blocked). Write to `.cliskill/discovery/ranked-analytics.md`.

```
cliskill ▸ DISCOVER ▸ ranking      Scoring and ranking...
cliskill ▸ DISCOVER ▸ done         Discovery complete — {N} Tier 1, {N} Tier 2, {N} Tier 3, {N} blocked
```

6. **Write state:**
```
.cliskill/state.md:
  phase: DISCOVER
  status: pending_review
  mode: discover
  capability_sources: [{list}]
  knowledge_sources: [{list}]
```

### DISCOVERY REVIEW

Present the discovery report to the user (see `references/discovery-protocol.md` for full format):

```
## cliskill — Discovery Report

Capability sources analyzed: {N} ({list})
Knowledge sources analyzed: {N} ({list})

What this repo can do: {summary}
What the reference material teaches: {summary}

Recommended Analytics (Tier 1 — quick wins):
  1. {name} — {why} — {effort}
  2. ...

Worth Building (Tier 2):
  3. {name} — {why} — {effort}
  ...

Stretch Goals (Tier 3):
  5. {name} — {why} — {effort}
  ...

Blocked:
  7. {name} — {blocker}

Select analytics for the skill:
1. All Tier 1 + Tier 2 (recommended)
2. All Tier 1 only (minimal viable skill)
3. Custom selection — pick specific analytics by number
4. Everything feasible (Tiers 1-3)
```

Wait for user response. Record their selection in `.cliskill/discovery/ranked-analytics.md`.

### Transition to SPECIFY

After the user selects analytics, proceed to Phase 1: SPECIFY with enriched context:

1. Pass the original references (repo, PDFs) to `/clarity` as usual.
2. Additionally pass the discovery artifacts as structured context:
   - `.cliskill/discovery/capabilities.md` — so clarity knows what the repo already has
   - `.cliskill/discovery/knowledge.md` — so clarity has precise method definitions
   - `.cliskill/discovery/ranked-analytics.md` — so clarity knows what to spec (the selected analytics only)
3. Clarity generates the spec scoped to the selected analytics, with requirements that reference existing repo capabilities where possible.
4. The skill brief includes a `## Discovery Context` section summarizing which analytics were selected, what repo capabilities each builds on, and what knowledge source defines the method.

Update state:
```
.cliskill/state.md:
  phase: SPECIFY
  status: in_progress
  mode: discover
  selected_analytics: [{list of selected names}]
```

From here, the pipeline follows the standard flow: SPECIFY → Review Gate 1 → BUILD → VERIFY → DEPLOY.

---

## Phase R: RESEARCH (conditional)

**Entry:** `/cliskill research <capability-refs> [-- <knowledge-refs>]`

**Load:** `references/research-protocol.md`, `references/discovery-protocol.md`

Research mode handles continuous optimization — the loop doesn't terminate on "pass" but keeps running as long as the metric is converging. It uses DISCOVER + metric negotiation + the autoresearch optimization loop (PROPOSE → RUN → CLASSIFY → KEEP/REVERT), with cliskill's rigor: failure classification, convergence detection, and guided escalation.

### Instructions

1. **DISCOVER.** Run the standard discovery pipeline (Phase D) to inventory capabilities and extract methods from knowledge sources. The discovery report's ranked capabilities inform which strategy classes to prioritize.

2. **NEGOTIATE.** Metric-compiler conversation with the human:
   - Ask 5 scenario questions to understand what "better" means
   - Propose 2 candidate metrics with tradeoff explanations
   - Human picks the metric (or defines their own)

3. **BOOTSTRAP.** Generate `program.md` + `metric.py` + `eval_harness.py`. Dry-run 2–3 experiments to verify the loop works end-to-end. Run metric verification against known-good and known-bad cases before entering OPTIMIZE.

4. **OPTIMIZE.** The autoresearch loop — PROPOSE → RUN → CLASSIFY → KEEP/REVERT. Experiments are classified per the decision tree in `references/research-protocol.md`. The loop runs until convergence stalls (see convergence detection rules in the reference).

5. **REVIEW.** Present results interactively: best model, strategy summary, Pareto front, recommendations. Human picks: continue, refine metric, or accept current best.

### State

```
.cliskill/state.md:
  mode: research
  phase: {DISCOVER | NEGOTIATE | BOOTSTRAP | OPTIMIZE | REVIEW}
  status: {in_progress | pending_review | stalled | complete}
  metric_name: {name}
  metric_score_best: {score}
  metric_score_baseline: {score}
  experiment_count: {N}
  kept_count: {M}
  current_strategy_class: {name}
  exhausted_classes: [{list}]
  last_5_outcomes: [{list}]
```

See `references/research-protocol.md` for the full protocol: experiment classification decision tree, strategy class tracking, convergence detection, metric verification, guided review format, and loop invariants.

---

## Phase 0: UPDATE (conditional)

**Entry:** `/cliskill update <existing-skill-path> <new-reference-1> [...]`

Update mode modifies an existing cliskill-produced skill when the underlying API has changed, new endpoints have been added, or behavior needs to evolve. It avoids starting from scratch by diffing against the existing spec and preserving what already works.

### Prerequisites

The target skill must have been produced by cliskill (i.e., `.clarity/spec.md` and `scenarios/` exist alongside it). If not, suggest a fresh `/cliskill` run instead.

### Instructions

1. Read the existing spec at `.clarity/spec.md` and the existing skill brief at `.clarity/skill-brief.md`.
2. Read the existing holdout scenarios in `scenarios/`.
3. Pass the **new references** to `/clarity` in INGEST mode, producing `.clarity/update-context.md`.
4. Diff the new context against the existing spec:

```
cliskill ▸ UPDATE ▸ diffing      Comparing new references against existing spec...
```

5. Classify each difference:

| Change Type | Description |
|---|---|
| **New capability** | API endpoint/feature not in current spec |
| **Changed behavior** | Existing endpoint changed parameters, response format, or semantics |
| **Deprecated** | Endpoint removed or marked deprecated |
| **Unchanged** | No difference from current spec |

6. Present the update plan to the user:

```
## cliskill — Update Plan

Existing skill: {skill-name}
Current spec: {N} requirements, {N} scenarios

### Changes detected

| # | Type | Description |
|---|------|-------------|
| 1 | New capability | POST /v2/batch-forecast endpoint |
| 2 | Changed behavior | GET /forecast now requires `units` parameter (was optional) |
| 3 | Deprecated | GET /forecast/legacy removed in v2 |

### What will happen

- {N} new requirement(s) will be added to the spec
- {N} existing requirement(s) will be updated
- {N} requirement(s) will be marked deprecated
- {N} new holdout scenario(s) will be created
- All {N} existing scenarios will be re-run to catch regressions

**Options:**
1. **Approve** — proceed with all changes
2. **Select** — choose which changes to include
3. **Cancel** — keep the skill as-is
```

7. On approval, delegate to `/clarity` to:
   - Update `.clarity/spec.md` with new/changed requirements (preserving existing FR-NNN numbering, appending new ones)
   - Add new holdout scenarios for new/changed behavior (preserving existing SC-NNN files)
   - Regenerate `.clarity/skill-brief.md`

8. Write state and proceed to Phase 2: BUILD:
```
.cliskill/state.md:
  phase: BUILD
  status: in_progress
  loop_count: 0
  mode: update
  previous_spec_hash: {hash of spec before update}
  changes: [list of change descriptions]
```

### Update-specific verification

During VERIFY, **all** scenarios are tested — both existing and new. This catches regressions where a change to support new behavior breaks existing behavior. The status line highlights this:

```
cliskill ▸ VERIFY ▸ starting     Running {N} scenarios ({M} existing + {K} new)...
cliskill ▸ VERIFY ▸ SC-001       ✓ Basic forecast retrieval (existing)
cliskill ▸ VERIFY ▸ SC-009       ✓ Batch forecast (new)
cliskill ▸ VERIFY ▸ SC-003       ✗ Invalid location handling (existing, regression)
```

Regressions in existing scenarios are classified as Implementation Gaps and prioritized in the repair loop.

---

## Phase V: VIBE

**Entry:** Runs automatically as the first step of every pipeline invocation (standard, discover, research, update). Not applicable to `/cliskill self-improve` or `/cliskill resume`.

The vibe phase converts the human's raw intent into a **vibe contract** — 3–5 binary (yes/no) checks that define success for the entire pipeline. The contract is always generated, but **the human only sees it when it matters**.

### Why This Exists

The vibe contract is invisible infrastructure — like a seatbelt that only locks when you brake hard. When the intent is clear ("wrap this API"), the checks are obvious and the human doesn't need to approve them. When the intent is ambiguous ("make this better"), the checks need human judgment. The phase adapts accordingly.

### Instructions

1. **Analyze the request.** Read the user's message, references, and inferred mode. Understand what they're trying to achieve — not what they literally said, but what success looks like.

```
cliskill ▸ VIBE ▸ starting       Analyzing request...
```

2. **Generate 3–5 binary checks.** Each check must be:
   - **Yes/no answerable** — no scales, no "partially"
   - **Verifiable from the output** — an agent can check it without the human
   - **Meaningful** — failing this check means the skill is wrong, not just imperfect

3. **Classify confidence: silent or interactive?**

```
SIGNAL → SILENT (auto-approve, don't present to human):
  - Clear, specific references (API docs with endpoints, structured specs)
  - Unambiguous goal ("wrap this API", "turn these docs into a CLI")
  - Standard mode with well-defined input
  - All generated checks are directly derivable from the references
    (the references make the checks obvious — no judgment needed)

SIGNAL → INTERACTIVE (present checks, wait for approval):
  - Vague or open-ended goal ("make this better", "what can I build?")
  - Discover or research mode (goal is exploratory)
  - Mixed references where the scope isn't obvious
  - User explicitly asked for input ("let me review", "what will you build?")
  - Any check that requires domain knowledge the references don't contain
```

4. **Route by confidence.**

**SILENT path (zero friction):**

```
cliskill ▸ VIBE ▸ checks         {N} checks generated (auto-approved — intent clear)
cliskill ▸ VIBE ▸ done           Proceeding autonomously
```

Write the vibe contract to `.cliskill/vibe-contract.md` with `approval: auto` and proceed immediately. The checks are logged but never presented. If a downstream vibe-check fails (spec doesn't cover a check), the contract surfaces at that point — the human sees it for the first time only when there's a problem.

**INTERACTIVE path (one touchpoint):**

```
cliskill ▸ VIBE ▸ checks         {N} checks generated — need your input
```

Present to the user:

```
## cliskill — Vibe Contract

Before I build anything, let's lock in what success looks like.

Based on your request, here's what I'd measure:

1. ☐ {check 1 — e.g., "Skill covers at least 5 analytics from the textbook"}
2. ☐ {check 2 — e.g., "All analytics verified against textbook formulas"}
3. ☐ {check 3 — e.g., "RMSE improves over baseline"}

Thumbs up, or veto any that are wrong?
```

Wait for response. The human's job is minimal:
   - 👍 or "go" — accept all checks
   - Veto specific checks — "not 3, I care about Pearson r not RMSE"
   - Add one — "also: must handle missing data"

```
cliskill ▸ VIBE ▸ approved       {N}/{N} checks approved — vibe contract locked
cliskill ▸ VIBE ▸ done           Proceeding autonomously
```

5. **Lock the vibe contract.** Write to `.cliskill/vibe-contract.md`:

```markdown
# Vibe Contract

locked: {ISO 8601}
approval: {auto | human}
mode: {standard | discover | research | update}
source: {user's original request, abbreviated}

## Checks

1. [description] — status: pending
2. [description] — status: pending
3. [description] — status: pending
```

6. **Proceed to the next phase** (DISCOVER, RESEARCH, SPECIFY, or UPDATE depending on mode detection).

### The Silent Path in Action

```
User: /cliskill https://api.stripe.com/docs

cliskill ▸ DETECT ▸ intent       Detected: STANDARD mode
cliskill ▸ VIBE ▸ starting       Analyzing request...
cliskill ▸ VIBE ▸ checks         4 checks generated (auto-approved — intent clear)
cliskill ▸ VIBE ▸ done           Proceeding autonomously
cliskill ▸ SPECIFY ▸ starting    Delegating to /clarity with 1 reference(s)
...pipeline runs to completion...
cliskill ▸ DEPLOY ▸ done         Deployed to claude, copilot, cursor
```

No interaction. One command in, deployed skill out. The vibe contract (`"covers all documented endpoints"`, `"JSON output on all commands"`, `"error responses include Stripe error codes"`, `"handles pagination"`) was generated, verified against the spec, and satisfied — all silently.

If the spec had missed pagination, the user would have seen:
```
cliskill ▸ SPECIFY ▸ vibe-check   ✗ Check 4 not covered: "handles pagination"
```
And *only then* would the contract surface for the first time.

### How the Vibe Contract Replaces Review Gates

**Review Gate 1 (spec approval):** After SPECIFY completes, cliskill checks each vibe contract item against the generated spec:

- Can every check be verified by at least one holdout scenario?
- Does the spec contain requirements that support every check?

If all checks are satisfied → **auto-approve**, notify the user:
```
cliskill ▸ SPECIFY ▸ vibe-check   Checking spec against vibe contract...
cliskill ▸ SPECIFY ▸ vibe-check   ✓ All {N} vibe checks covered by spec
cliskill ▸ SPECIFY ▸ auto-approve Proceeding to BUILD (vibe contract satisfied)
```

If any check is NOT covered → **stop and present the gap**:
```
cliskill ▸ SPECIFY ▸ vibe-check   ✗ Check {N} not covered: "{description}"
```
Then present the gap to the user with options to adjust the spec or revise the check.

**Review Gate 2 (deployment approval):** After VERIFY passes all scenarios, the gate auto-approves:
```
cliskill ▸ DEPLOY ▸ vibe-check    All scenarios passed + vibe contract satisfied
cliskill ▸ DEPLOY ▸ auto-approve  Deploying (vibe contract satisfied)
```

The user is notified but not blocked. If they want to stop deployment, they can — but the default is go.

### Vibe Contract Invariants

- The contract is **write-once**. Once locked, checks cannot be added, removed, or weakened. If the vibe was wrong, the user starts a new pipeline.
- The contract is **the source of truth** for auto-approval. No other signal overrides it.
- The contract lives in `.cliskill/vibe-contract.md` alongside pipeline state.
- For `/cliskill resume`, the existing contract is reloaded — never re-negotiated.

---

## Phase 1: SPECIFY

**Delegate to:** `/clarity` (phases 1–4: INGEST, SPECIFY, SCENARIO, HANDOFF)

### Instructions

1. Pass all user-provided references to `/clarity`, along with the vibe contract from `.cliskill/vibe-contract.md` so that clarity can ensure the spec covers the success checks.
2. Let clarity run its full pipeline through HANDOFF:
   - **INGEST**: Consume references → `.clarity/context.md`
   - **SPECIFY**: Generate structured spec → `.clarity/spec.md`
   - **SCENARIO**: Create holdout scenarios → `scenarios/SC-*.md`
   - **HANDOFF**: Generate skill brief → `.clarity/skill-brief.md`
3. Write state:
   ```
   .cliskill/state.md:
     phase: SPECIFY
     status: pending_review
     loop_count: 0
     started: {ISO timestamp}
   ```

### REVIEW GATE 1: Specification Review (conditional)

**First, check the vibe contract.** For each check in `.cliskill/vibe-contract.md`, verify:
- At least one requirement in the spec supports this check
- At least one holdout scenario tests this check

```
cliskill ▸ SPECIFY ▸ vibe-check   Checking spec against vibe contract...
```

**If ALL vibe checks are covered → auto-approve:**

```
cliskill ▸ SPECIFY ▸ vibe-check   ✓ All {N} vibe checks covered by spec
cliskill ▸ SPECIFY ▸ auto-approve Proceeding to BUILD — spec: {N} requirements, {N} scenarios
```

Update each check's status to `covered` in `vibe-contract.md`. Proceed directly to BUILD. The user is notified but not blocked.

**If ANY vibe check is NOT covered → stop and present:**

```
## cliskill — Spec vs. Vibe Gap

Clarity produced {N} requirements and {N} scenarios, but {M} vibe check(s) aren't covered:

✗ Check {N}: "{description}"
  Missing: {no requirement addresses this | no scenario tests this}

✓ Check {N}: "{description}" — covered by FR-{NNN}, SC-{NNN}

**Options:**
1. **Fix spec** — add requirements to cover the gap (re-run SPECIFY with guidance)
2. **Drop the check** — remove it from the vibe contract (the vibe was wrong)
3. **Review manually** — show me the full spec, I'll decide
```

Wait for user response. This is the only case where Review Gate 1 blocks.

On approval, update state:
```
.cliskill/state.md:
  phase: BUILD
  status: in_progress
  loop_count: 0
```

---

## Phase 2: BUILD

**Delegate to:** `/agent-skill-creator`

### Instructions

1. Read `.clarity/skill-brief.md`.
2. If this is a rebuild (loop_count > 0), also read `.cliskill/loop-{N}/changes.md` for rebuild context.
3. Invoke `/agent-skill-creator` with the skill brief:
   - Agent-skill-creator skips Phase 1 (Discovery) and Phase 2 (Design) — the brief has those decisions.
   - It runs Phase 3 (Architecture), Phase 4 (Detection), Phase 5 (Implementation).
4. Agent-skill-creator's built-in validation must pass (SKILL.md structure, security scan).
5. If validation fails, treat as an implementation issue and let agent-skill-creator fix it (this is within its own pipeline, not cliskill's loop).
6. **Generate eval harness.** After the skill build completes successfully:
   - Generate `{skill-dir}/_optimize/eval.py` from the holdout scenarios — a script that runs each scenario programmatically and outputs `{"pass_rate": N, "quality_score": null, "scenarios": {...}}`.
   - Generate `{skill-dir}/_optimize/program.md` from the template in `references/self-improvement-protocol.md` §3, filled with skill-specific details (name, editable files, strategy classes).
   - See `references/self-improvement-protocol.md` §3 for format details.

```
cliskill ▸ BUILD ▸ eval-harness   Generating _optimize/eval.py from {N} scenarios...
cliskill ▸ BUILD ▸ eval-harness   Generating _optimize/program.md...
cliskill ▸ BUILD ▸ eval-harness   Done — eval harness ready
```

7. Update state:
   ```
   .cliskill/state.md:
     phase: VERIFY
     status: in_progress
     loop_count: {current}
   ```

### Rebuild Context

When loop_count > 0, append rebuild context to the skill brief before passing to agent-skill-creator. See `references/evaluation-router.md` for the rebuild context template.

---

## Phase 3: VERIFY

**Delegate to:** `/clarity evaluate`

### Instructions

1. Load `references/evaluation-router.md`.
2. Run `/clarity evaluate` against the built skill, using the holdout scenarios in `scenarios/`.
3. Clarity produces an evaluation report at `.clarity/evaluations/eval-{date}.md`.
4. Parse the evaluation report:

**If ALL scenarios PASS:**
- **Establish optimization baseline.** Run `{skill-dir}/_optimize/eval.py`, write results to `{skill-dir}/_optimize/baseline.md`, and initialize `{skill-dir}/_optimize/results.tsv` with a baseline row. See `references/self-improvement-protocol.md` §3 for formats.

```
cliskill ▸ VERIFY ▸ baseline      Running eval.py for optimization baseline...
cliskill ▸ VERIFY ▸ baseline      pass_rate: {v}, quality_score: {v}
cliskill ▸ VERIFY ▸ baseline      Baseline written to _optimize/baseline.md
```

- Update state:
  ```
  .cliskill/state.md:
    phase: DEPLOY
    status: pending_review
    loop_count: {current}
    result: all_pass
  ```
- Proceed to Phase 4: DEPLOY.

**If any scenarios FAIL:**
- Enter REPAIR LOOP (see below).

**If all failures are Scenario Gaps (no spec or implementation failures):**
- Escalate to user — holdout tests may need updating.
- Do NOT auto-fix scenarios.

---

## REPAIR LOOP

**Load:** `references/evaluation-router.md`, `references/loop-protocol.md`

### Entry Conditions

- One or more scenarios failed in VERIFY.
- Current loop_count < 3.

### Loop Logic

```
loop_count += 1

# Save loop artifacts
create .cliskill/loop-{loop_count}/
copy eval report → .cliskill/loop-{loop_count}/eval-report.md
if loop_count > 1: read .cliskill/loop-{loop_count-1}/diff.md to avoid repeating failed fixes

# Classify each failure (see references/evaluation-router.md)
# IMPORTANT: When ambiguous, default to Spec Gap. The cost of an unnecessary
# spec update (one extra loop) is far lower than the cost of a missed spec gap
# (all three loops wasted patching code with the wrong spec underneath).
for each failure in eval report:
    classify as: Spec Gap | Implementation Gap | Scenario Gap
    record classification in .cliskill/loop-{loop_count}/changes.md

# Route by failure type
if ONLY Scenario Gaps:
    → guided escalation (scenario_gap)

if any Spec Gaps present:
    # Fix spec first — impl gaps may self-resolve
    for each Spec Gap:
        update .clarity/spec.md with missing/corrected requirement
    regenerate .clarity/skill-brief.md from updated spec
    record all spec changes in .cliskill/loop-{loop_count}/changes.md
    write structured diff to .cliskill/loop-{loop_count}/diff.md
    → go to Phase 2: BUILD

if ONLY Implementation Gaps:
    # Generate targeted fix prompt
    create rebuild context (see references/evaluation-router.md)
    append rebuild context to .cliskill/loop-{loop_count}/changes.md
    write structured diff to .cliskill/loop-{loop_count}/diff.md
    → go to Phase 2: BUILD with rebuild context

# Convergence check
if same failure persists for 2 consecutive loops:
    → guided escalation (no_convergence)

# Loop exhaustion
if loop_count >= 3:
    → guided escalation (max_loops)
```

Update state after each loop iteration:
```
.cliskill/state.md:
  phase: BUILD (or VERIFY after rebuild)
  status: in_progress
  loop_count: {current}
  last_failure_ids: [SC-xxx, SC-yyy]
```

---

## Guided Escalation

When the repair loop needs human input, don't dump a wall of diagnostics. Walk the user through each failure interactively, one at a time, with clear options.

### Escalation Flow

For each failure requiring attention, present it individually:

```
## cliskill — Needs Your Input ({current}/{total} failures)

**Loop:** {N} of 3 | **Reason:** {scenario_gap | no_convergence | max_loops}

### SC-{NNN}: {scenario title}

**What I expected:** {expected behavior from scenario}
**What happened:** {actual behavior from eval}
**My classification:** {Spec Gap | Implementation Gap | Scenario Gap}
**Why I think so:** {1-2 sentence reasoning}

**Options:**
1. **Agree with my classification** — I'll {describe what the auto-fix would do}
2. **Reclassify** — tell me the actual root cause
3. **The test is wrong** — update scenario SC-{NNN} (you edit, I'll re-run)
4. **Show me the code** — see the relevant implementation before deciding
5. **Skip this one** — move to the next failure
```

Wait for user response before presenting the next failure.

### Rules

- **One failure at a time.** Never present all failures in a single block. The user should focus on one decision.
- **Lead with your best guess.** Always show your classification and reasoning — the user is confirming or correcting, not starting from scratch.
- **Option 4 is always available.** The user may need to see the implementation to decide. Show the relevant code section (not the whole file), then re-present the options.
- **After all failures are resolved**, summarize the plan before executing:

```
## cliskill — Escalation Summary

Resolved {N} failure(s):
- SC-{NNN}: {classification} → {action}
- SC-{NNN}: {classification} → {action}
- SC-{NNN}: Scenario updated by user

**Next step:** {Rebuild with fixes | Re-run verification | Done}

Proceed? (yes / adjust)
```

- **On user reclassification**, update `.cliskill/loop-{N}/changes.md` with the user's classification and reasoning. This prevents the same misclassification on resume.
- **On scenario update**, the user edits the scenario file directly. cliskill re-runs verification after all edits are complete. The holdout-is-sacred rule still holds — only the human touches scenarios.

### Escalation by Reason

| Reason | Guided behavior |
|---|---|
| **scenario_gap** | Present each scenario gap. Default option: "The test is wrong." User edits scenario, then `/cliskill resume`. |
| **no_convergence** | Present the stuck failure with full loop history (what was tried in each loop). Default option: "Show me the code." |
| **max_loops** | Present all remaining failures. Summarize what each loop attempted. Default option: "Reclassify" (the classification was likely wrong). |

### Status Lines

```
cliskill ▸ ESCALATE ▸ starting   {N} failure(s) need your input
cliskill ▸ ESCALATE ▸ SC-{NNN}   Waiting for input...
cliskill ▸ ESCALATE ▸ SC-{NNN}   Resolved: {classification} → {action}
cliskill ▸ ESCALATE ▸ done       {N} resolved — {next step}
```

---

## Phase 4: DEPLOY

### REVIEW GATE 2: Deployment Review (auto-approve)

All scenarios passed. The vibe contract is satisfied. Auto-approve and deploy.

```
cliskill ▸ DEPLOY ▸ vibe-check    All scenarios passed + vibe contract satisfied
cliskill ▸ DEPLOY ▸ auto-approve  Deploying to detected platforms
```

Notify the user (non-blocking):

```
## cliskill — Deploying

✓ {N}/{N} holdout scenarios passed {loop info if applicable}
✓ Vibe contract satisfied ({N}/{N} checks)

Deploying {skill-name} to {platform list}...
```

The user can still intervene — if they say "wait" or "stop" before deployment completes, abort. But the default is go. The human approved the vibe; the machine verified the rest.

### On Deploy

1. **Log build metrics.** Load `references/self-improvement-protocol.md`. Append a row to `~/acc/cliskill/.cliskill-meta/results.tsv` with this build's outcome (date, skill_name, mode, scenario_count, loop_count, first_pass, escalated, escalation_reason, notes). Create the file with header if it doesn't exist. See §2 of the protocol for field definitions.

```
cliskill ▸ DEPLOY ▸ metrics       Logging build outcome to .cliskill-meta/results.tsv
cliskill ▸ DEPLOY ▸ metrics       Build #{N}: {first_pass | loops: N | escalated}
```

2. Use agent-skill-creator's auto-install to deploy the skill to all detected platforms.
3. Offer team sharing options (git remote, registry).
4. Update state:
   ```
   .cliskill/state.md:
     phase: COMPLETE
     status: deployed
     loop_count: {final}
     platforms: [list of installed platforms]
   ```

### Completion Summary

```
## cliskill — Complete

✓ Specified: {N} requirements, {N} holdout scenarios
✓ Built: {skill-name} ({N} files)
✓ Verified: {N}/{N} scenarios passed {loop info if applicable}
✓ Deployed to: {platform list}
✓ Optimization: _optimize/ ready (baseline pass_rate: {v})

Artifacts:
  .clarity/           — spec, context, skill brief, evaluations
  .cliskill/          — pipeline state and loop history
  scenarios/          — holdout scenarios
  {skill-directory}/  — the deployed skill
  {skill-directory}/_optimize/  — eval harness for post-deployment optimization
```

---

## Phase S: SELF-IMPROVE

**Entry:** `/cliskill self-improve`

**Load:** `references/self-improvement-protocol.md`

Self-improve mode reads cliskill's accumulated build metrics and proposes changes to cliskill's own instructions to improve build efficiency. It does not build a skill — it improves the tool that builds skills.

### Prerequisites

- `~/acc/cliskill/.cliskill-meta/results.tsv` must exist with at least 5 rows.
- No active experiment (`.cliskill-meta/current-experiment.md` must be empty or absent).

If prerequisites aren't met:

```
cliskill ▸ SELF-IMPROVE ▸ blocked    Need {5 - N} more builds before self-improvement can run
```

### Instructions

1. **Read metrics.** Load `results.tsv`, compute `first_pass_rate`, `avg_repair_loops`, `escalation_rate`.

```
cliskill ▸ SELF-IMPROVE ▸ starting     Loading build history ({N} builds)
cliskill ▸ SELF-IMPROVE ▸ metrics      first_pass_rate: {v}, avg_loops: {v}, escalation_rate: {v}
```

2. **Check for active experiment.** If `current-experiment.md` exists:
   - If builds_since >= 5: classify the experiment (KEEP/REVERT/DESTRUCTIVE), record in `experiments.tsv`, clear `current-experiment.md`.
   - If builds_since < 5: report status and stop.

```
cliskill ▸ SELF-IMPROVE ▸ experiment   Active experiment E-{NNN}: {classifying... | waiting, {N} more builds needed}
cliskill ▸ SELF-IMPROVE ▸ classify     E-{NNN}: {KEEP | REVERT | INCONCLUSIVE} — {metric}: {before} → {after}
```

3. **Identify weakest metric.** Follow the decision tree in `self-improvement-protocol.md` §2.

```
cliskill ▸ SELF-IMPROVE ▸ metrics      Weakest: {metric name} ({value})
```

4. **Hypothesize change.** Read the target file, identify a specific, targeted improvement. Write the hypothesis to `current-experiment.md`.

5. **Present to user.**

```
## cliskill — Self-Improvement Proposal

### Current Metrics (over {N} builds)

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| first_pass_rate | {v} | > 0.6 | {✓ / ✗} |
| avg_repair_loops | {v} | < 1.5 | {✓ / ✗} |
| escalation_rate | {v} | < 0.3 | {✓ / ✗} |

### Weakest Metric: {name}

**Hypothesis:** {what we think will improve it}
**Target file:** {path}
**Proposed change:** {description of the edit}

**Options:**
1. **Approve** — apply the change, measure over next 5 builds
2. **Modify** — adjust the hypothesis before applying
3. **Skip** — no changes right now
```

Wait for user response.

6. **On approval:** Apply the change, commit with message `self-improve: {hypothesis summary}`, update `current-experiment.md` with the commit SHA.

```
cliskill ▸ SELF-IMPROVE ▸ applied      Change committed: {sha}
cliskill ▸ SELF-IMPROVE ▸ done         Experiment E-{NNN} active — will classify after 5 builds
```

---

## Error Handling

| Situation | Action |
|-----------|--------|
| `/clarity` not installed | Auto-install via `check_deps.py`; if auto-install fails, print manual instructions and stop |
| `/agent-skill-creator` not installed | Auto-install via `check_deps.py`; if auto-install fails, print manual instructions and stop |
| Clarity fails mid-phase | Save partial state, allow `/cliskill resume` |
| Agent-skill-creator validation fails repeatedly | Escalate — likely a spec issue masquerading as impl failure |
| Network error during reference ingestion | Retry once, then ask user for local copy |
| `.cliskill/state.md` corrupted | Ask user to delete `.cliskill/` and restart |

---

## State Directory Structure

```
.cliskill/
├── state.md              # Current phase, loop count, status, mode
├── vibe-contract.md      # Success checks locked during VIBE phase
├── discovery/            # Only present in discover mode
│   ├── capabilities.md   # Phase D1: repo inventory (with file:line evidence)
│   ├── knowledge.md      # Phase D2: methods from knowledge sources
│   ├── cross-reference.md # Phase D3: feasibility matrix (post-probe)
│   ├── probes.md         # Feasibility probe results per method
│   └── ranked-analytics.md # Phase D4: ranked list + user selection
├── loop-1/
│   ├── eval-report.md    # Evaluation results for this iteration
│   ├── changes.md        # What was fixed (classifications + actions)
│   └── diff.md           # Structured diff of what changed (spec or skill)
├── loop-2/
│   └── ...
└── loop-3/
    └── ...
```

### cliskill Self-Improvement State (persistent, across builds)

```
~/acc/cliskill/.cliskill-meta/
├── results.tsv              # Build outcomes — append-only, one row per build
├── experiments.tsv           # Self-improvement experiment log — append-only
├── current-experiment.md     # Active experiment details (empty if none)
└── metrics-snapshot.md       # Last computed aggregate metrics
```

### Per-Skill Optimization Harness (generated during BUILD)

```
{skill-name}/
├── ...                       # Existing skill files
└── _optimize/
    ├── program.md            # Autoresearch instructions for this skill
    ├── eval.py               # Evaluation harness (READ-ONLY post-deployment)
    ├── baseline.md           # Initial build scores (written during VERIFY)
    └── results.tsv           # Experiment log (initialized during DEPLOY)
```

All loop artifacts are preserved for debugging. Never delete previous loop data during a run.
