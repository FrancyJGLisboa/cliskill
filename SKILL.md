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
  end-to-end skill pipeline, create and verify skill.
license: MIT
metadata:
  author: Francy Lisboa Charuto
  version: 1.0.0
  created: 2026-03-13
  last_reviewed: 2026-03-13
  review_interval_days: 90
---

# cliskill — AI-Agent-Friendly CLI Skill Framework

> Point at API references. Get a verified CLI tool that agents know how to wield.

cliskill is a closed-loop pipeline that transforms API references into production-ready CLI tools — tools that AI agents fully understand: how to use them, when to use them, when not to, and when to honestly give up. It delegates specification to `/clarity`, implementation to `/agent-skill-creator`, and adds what neither has: an **automated evaluation-fix-rebuild loop**.

The human provides references and reviews twice. Everything else is autonomous.

## Trigger

```
/cliskill <reference-1> [<reference-2> ...]
/cliskill resume
```

References can be: API documentation, repository URLs, file paths, PDFs, URLs, or free-text descriptions — anything `/clarity` can ingest.

**Examples:**
```
/cliskill https://api.example.com/docs https://github.com/example/weather-api
/cliskill ./specs/finnhub-api-reference.pdf
/cliskill resume
```

## Core Principles

1. **Two review gates, not more.** The human approves the spec (after SPECIFY) and the deployment (after VERIFY). Everything between is autonomous.
2. **Holdout scenarios are sacred. This is a hard constraint, not a guideline.** Never auto-fix a failing holdout test. Never weaken a scenario to make it pass. If the test is wrong, that's a Scenario Gap — escalate to the human. If cliskill ever auto-patches holdout scenarios, the entire verification primitive collapses.
3. **Three loops maximum.** If the evaluation-fix cycle hasn't converged in 3 iterations, escalate with full diagnostics. Don't spin.
4. **Fix spec first.** When both spec and implementation gaps exist, fix the spec first — implementation gaps often self-resolve when the spec is corrected.
5. **Preserve passing behavior.** Rebuilds target only failing scenarios. Never re-architect what already works.
6. **State is resumable.** Every phase writes state to `.cliskill/`. If interrupted, `/cliskill resume` picks up where it left off.
7. **Agent-native output.** The produced CLI skill must be fully understandable by AI agents — clear activation triggers, explicit limitations, honest failure modes, and well-defined anti-goals.

## Reference Files

Load these on demand when entering the relevant phase:

| File | Load when |
|------|-----------|
| `references/evaluation-router.md` | Entering VERIFY phase or REPAIR LOOP |
| `references/loop-protocol.md` | Entering REPAIR LOOP or processing `/cliskill resume` |
| `references/examples.md` | When needing pattern reference for any phase |

## Dependencies

cliskill orchestrates two existing skills. Both must be installed:

- **`/clarity`** — Specification engine (INGEST → SPECIFY → SCENARIO → HANDOFF → EVALUATE)
- **`/agent-skill-creator`** — Implementation engine (Discovery → Design → Architecture → Detection → Implementation)

Run `python3 scripts/check_deps.py` to verify both are available.

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
if .cliskill/state.md exists AND command is "/cliskill resume":
    read state.md → determine current phase and loop count
    resume from recorded phase
else if .cliskill/state.md exists AND command is "/cliskill <refs>":
    warn: "Found existing .cliskill/ state. Resume with /cliskill resume or delete .cliskill/ to start fresh."
    stop
else:
    start Phase 1: SPECIFY
```

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
    escalate to human:
        "All failures are Scenario Gaps. Holdout tests may need updating.
         Review the eval report and adjust scenarios, then /cliskill resume."
    update state: status = escalated_scenario_gap
    STOP

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
    escalate to human:
        "Failure SC-{NNN} has not converged after 2 attempts.
         Manual intervention needed. See .cliskill/loop-{N}/ for diagnostics."
    update state: status = escalated_no_convergence
    STOP

# Loop exhaustion
if loop_count >= 3:
    escalate to human:
        "Maximum repair loops (3) exhausted. {N} failures remain.
         See .cliskill/ for full diagnostic history."
    update state: status = escalated_max_loops
    STOP
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
| `/clarity` not installed | Print install instructions, stop |
| `/agent-skill-creator` not installed | Print install instructions, stop |
| Clarity fails mid-phase | Save partial state, allow `/cliskill resume` |
| Agent-skill-creator validation fails repeatedly | Escalate — likely a spec issue masquerading as impl failure |
| Network error during reference ingestion | Retry once, then ask user for local copy |
| `.cliskill/state.md` corrupted | Ask user to delete `.cliskill/` and restart |

---

## State Directory Structure

```
.cliskill/
├── state.md              # Current phase, loop count, status
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
