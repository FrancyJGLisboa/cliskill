# Loop Protocol

Rules for the cliskill repair loop: state tracking, convergence detection, partial progress, and escalation.

---

## State Tracking

### `.cliskill/state.md` Format

```markdown
# cliskill Pipeline State

phase: {VIBE | SPECIFY | BUILD | VERIFY | DEPLOY | COMPLETE}
status: {in_progress | pending_review | auto_approved | escalated_scenario_gap | escalated_no_convergence | escalated_max_loops | deployed}
loop_count: {0-3}
started: {ISO 8601 timestamp}
last_updated: {ISO 8601 timestamp}
last_failure_ids: [{comma-separated SC-NNN IDs, empty if none}]
skill_name: {name of the skill being built, once known}
references: [{original reference paths/URLs}]
vibe_contract: .cliskill/vibe-contract.md
```

### `.cliskill/` Directory Structure

```
.cliskill/
├── state.md                 # Pipeline state (always present)
├── loop-1/                  # Created on first repair iteration
│   ├── eval-report.md       # Copy of evaluation report
│   ├── changes.md           # Classification + actions taken
│   └── diff.md              # Structured diff of what changed (spec or skill)
├── loop-2/                  # Created on second repair iteration
│   ├── eval-report.md
│   ├── changes.md
│   └── diff.md
└── loop-3/                  # Created on third repair iteration (max)
    ├── eval-report.md
    ├── changes.md
    └── diff.md
```

### `changes.md` Format

```markdown
# Loop {N} Changes

## Failure Classifications

| Scenario | Root Cause | Action |
|----------|-----------|--------|
| SC-{NNN} | {Spec Gap / Implementation Gap / Scenario Gap} | {description of action taken} |

## Spec Changes (if any)

{Diff or description of changes to .clarity/spec.md}

## Rebuild Context (if any)

{The rebuild context appended to the skill brief}

## Outcome

{Brief note: "Proceeding to BUILD" or "Escalating because..."}
```

### `diff.md` Format

A structured diff of what actually changed between this loop and the previous state. Serves two purposes: (1) makes escalation diagnostics clearer for humans, and (2) gives the next loop's agent explicit context about what was already tried, preventing it from generating the same fix twice.

```markdown
# Loop {N} Diff

## Spec Changes

{Unified diff of .clarity/spec.md, or "No spec changes this loop"}

## Skill Brief Changes

{Unified diff of .clarity/skill-brief.md, or "No brief changes this loop"}

## Skill Code Changes

{Summary of files added/modified/removed in the skill directory}
{For modified files: key changes in plain language, not full diffs}

## What Was Tried

{1-2 sentence summary of the fix strategy this loop attempted}

## Result

{Did it help? Which scenarios improved, which didn't?}
```

The next loop's agent MUST read the previous loop's `diff.md` before generating its fix strategy. This prevents repeating failed approaches.

---

## Resume Protocol

When `/cliskill resume` is invoked:

1. Read `.cliskill/state.md`.
2. Validate all expected artifacts exist for the recorded phase.
3. Resume based on status:

| State | Resume Action |
|-------|---------------|
| `phase: SPECIFY, status: in_progress` | Continue clarity pipeline |
| `phase: VIBE, status: pending_review` | Re-present vibe contract for approval |
| `phase: SPECIFY, status: pending_review` | Re-present spec for review (vibe gap detected) |
| `phase: SPECIFY, status: auto_approved` | Spec auto-approved — continue to BUILD |
| `phase: BUILD, status: in_progress` | Re-run build from skill brief |
| `phase: VERIFY, status: in_progress` | Re-run evaluation |
| `phase: DEPLOY, status: pending_review` | Re-present deployment review |
| `status: escalated_*` | Show escalation context, ask user for guidance |
| `phase: COMPLETE` | Report: "Pipeline already complete. Delete .cliskill/ to start fresh." |

If artifacts are missing for the recorded phase, fall back to the latest phase with complete artifacts.

---

## Convergence Rules

### Definition

The loop is **converging** if, after each iteration, at least one of:
- The number of failing scenarios decreases, OR
- A previously-failing scenario now passes (even if a new one fails), OR
- The root cause of a failure shifts (e.g., Spec Gap → Implementation Gap)

The loop is **not converging** if:
- The exact same scenario fails with the same root cause for 2 consecutive loops
- No net progress in failure count after a loop

### Actions

| Convergence State | Action |
|-------------------|--------|
| Converging | Continue to next loop iteration |
| Not converging (specific scenario) | Escalate that scenario; continue fixing others if possible |
| Not converging (all failures stuck) | Escalate entire pipeline |

---

## Partial Progress Rules

If a rebuild fixes some scenarios but introduces new failures:

1. **New failure in a previously-passing scenario**: This is a regression. Classify as Implementation Gap. The rebuild context for the next loop must explicitly state: "SC-{NNN} was passing before loop {N} and must continue to pass."

2. **New failure in a scenario that wasn't tested before**: Treat normally — classify and route.

3. **Previously-failing scenario now passes**: Record as progress. Remove from the fix target list.

---

## Escalation Protocol

Escalation uses **guided escalation** — an interactive, one-failure-at-a-time flow defined in the main SKILL.md under "Guided Escalation." The full protocol lives there. This section covers the loop-protocol-specific rules.

### State on Escalation

Update state immediately when entering escalation:
```
.cliskill/state.md:
  status: escalated_{reason}
  escalation_failures: [SC-NNN, SC-NNN]
  escalation_reason: {scenario_gap | no_convergence | max_loops}
```

### Resume After Escalation

When `/cliskill resume` is called after an escalation:

1. Read `.cliskill/state.md` — check `escalation_reason` and `escalation_failures`.
2. If the user edited scenario files, detect changes via file modification timestamps.
3. Re-run VERIFY on all scenarios (not just the escalated ones — edits may have side effects).
4. If all pass → proceed to DEPLOY.
5. If new failures appear → re-enter the repair loop (loop_count does NOT reset — the human intervention counts as a loop iteration).

### Diagnostic Artifacts

Even though escalation is now interactive, all artifacts are still written to disk for reference:

- Evaluation reports: `.cliskill/loop-{N}/eval-report.md`
- Change logs: `.cliskill/loop-{N}/changes.md` (includes user's reclassifications if any)
- Current spec: `.clarity/spec.md`
- Current skill: `{skill directory}`

---

## Loop Invariants

These must hold true throughout the repair loop:

1. **Holdout scenarios are read-only.** The loop never modifies files in `scenarios/`.
2. **Previous loop artifacts are immutable.** `.cliskill/loop-{N}/` is never modified after loop N+1 begins.
3. **State is always written before action.** If the process is interrupted, state.md reflects where to resume.
4. **Spec changes are additive.** New requirements are added; existing passing requirements are never removed or weakened.
5. **Each loop iteration produces a complete eval report.** No partial evaluations — always test all scenarios.
