---
name: cliskill
description: >-
  Framework for building AI-agent-friendly CLI tools. Point at API references —
  repos, URLs, docs, code — and get a verified, deployed agent skill packaged
  as a CLI that agents fully understand: how to use it, when to use it, when
  not to, and when to give up. Closed-loop pipeline: specify, build, evaluate,
  auto-fix, rebuild. Uses /clarity for specification and holdout verification,
  /agent-skill-creator for implementation and deployment.
  Triggers on: cliskill, build cli skill, agent-friendly cli, api to cli skill,
  end-to-end skill pipeline, create and verify skill, update existing skill,
  api changed update skill, discover what analytics are possible, turn repo
  into agent skill, cross-reference repo with course material.
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

> Point at API references. Get a verified CLI tool that agents know how to wield.

cliskill is a closed-loop pipeline that transforms API references into production-ready CLI tools — tools that AI agents fully understand: how to use them, when to use them, when not to, and when to honestly give up. It delegates specification to `/clarity`, implementation to `/agent-skill-creator`, and adds what neither has: an **automated evaluation-fix-rebuild loop**.

The human provides references and reviews twice. Everything else is autonomous.

## Trigger

```
/cliskill <reference-1> [<reference-2> ...]
/cliskill resume
/cliskill update <existing-skill-path> <new-reference-1> [<new-reference-2> ...]
/cliskill discover <capability-ref-1> [<capability-ref-2> ...] -- <knowledge-ref-1> [<knowledge-ref-2> ...]
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
```

The `--` separator in discover mode separates capability sources (repos, code, data) from knowledge sources (courses, textbooks, methodology docs). If omitted, the agent classifies each reference automatically.

## Core Principles

1. **Two review gates, not more.** The human approves the spec (after SPECIFY) and the deployment (after VERIFY). Everything between is autonomous.
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
| `references/examples.md` | When needing pattern reference for any phase |

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

On every invocation, check for existing state:

```
if command is "/cliskill discover <refs> [-- <knowledge-refs>]":
    → enter DISCOVER mode (see Phase D: DISCOVER below)

else if command is "/cliskill update <skill-path> <refs>":
    → enter UPDATE mode (see Phase 0: UPDATE below)

else if .cliskill/state.md exists AND command is "/cliskill resume":
    read state.md → determine current phase and loop count
    resume from recorded phase
else if .cliskill/state.md exists AND command is "/cliskill <refs>":
    warn: "Found existing .cliskill/ state. Resume with /cliskill resume or delete .cliskill/ to start fresh."
    stop
else:
    start Phase 1: SPECIFY
```

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

## Phase 1: SPECIFY

**Delegate to:** `/clarity` (phases 1–4: INGEST, SPECIFY, SCENARIO, HANDOFF)

### Instructions

1. Pass all user-provided references to `/clarity`.
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

### REVIEW GATE 1: Specification Review

Present to the user:

```
## cliskill — Specification Review

Clarity has produced:
- **Spec**: .clarity/spec.md ({N} requirements)
- **Scenarios**: {N} holdout scenarios in scenarios/
- **Skill Brief**: .clarity/skill-brief.md

Please review the spec and skill brief.

**Options:**
1. **Approve** — proceed to BUILD
2. **Redirect** — significant changes needed (re-run SPECIFY with guidance)
3. **Adjust** — minor tweaks (edit spec directly, then approve)
```

Wait for user response. Do not proceed until explicitly approved.

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
6. Update state:
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

### REVIEW GATE 2: Deployment Review

Present to the user:

```
## cliskill — Deployment Review

Skill verified against {N} holdout scenarios. All passed.
{If loops > 0: "Required {N} repair loop(s) to reach convergence."}

**Built skill:** {skill-name}
**Location:** {skill directory path}

**Options:**
1. **Deploy** — install to detected platforms
2. **Review first** — examine the skill before deploying
3. **Skip deployment** — keep the skill local, don't install
```

Wait for user response.

### On Deploy

1. Use agent-skill-creator's auto-install to deploy the skill to all detected platforms.
2. Offer team sharing options (git remote, registry).
3. Update state:
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

Artifacts:
  .clarity/           — spec, context, skill brief, evaluations
  .cliskill/          — pipeline state and loop history
  scenarios/          — holdout scenarios
  {skill-directory}/  — the deployed skill
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

All loop artifacts are preserved for debugging. Never delete previous loop data during a run.
