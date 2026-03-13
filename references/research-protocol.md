# Research Protocol

Rules for cliskill's RESEARCH mode: continuous optimization loops for models and pipelines, experiment classification, strategy tracking, convergence detection, and guided review.

---

## What Research Protocol Solves

Standard cliskill targets binary pass/fail — holdout scenarios either pass or they don't, and the loop terminates when all pass. Research protocol targets **continuous metrics** (lower RMSE, higher Pearson r, better F1). The loop doesn't terminate on "pass" — it keeps going as long as it's converging.

The relationship to other modes:

| Mode | Target | Terminates when |
|------|--------|----------------|
| Standard (BUILD → VERIFY → REPAIR) | Binary pass/fail on holdout scenarios | All scenarios pass or 3 loops exhausted |
| Discovery | Feasibility ranking | User selects analytics |
| **Research** | Continuous metric optimization | Convergence stalls or human accepts result |

Discovery finds what's feasible. Metric negotiation defines "better." Research protocol runs the optimization.

---

## Experiment Classification Decision Tree

Adapts evaluation-router.md's Spec/Impl/Scenario Gap classification to continuous optimization. For each experiment where the metric did NOT improve:

```
1. Did the experiment crash or error?
   ├── YES → Implementation Bug
   │        The idea might be sound but the code is broken.
   │        Action: Read error log. Fix bug. Rerun SAME experiment.
   │
   └── NO → continue
              │
              2. Did the metric get SIGNIFICANTLY worse (> 2σ from baseline)?
              ├── YES → Destructive Hypothesis
              │        The idea fundamentally harms the objective.
              │        Action: Revert. Log as "destructive." Never retry this class of change.
              │
              └── NO → continue
                         │
                         3. Is this the Nth attempt in the same idea class?
                         ├── YES (N ≥ 3) → Exhausted Direction
                         │        This direction has been explored enough.
                         │        Action: Revert. Log. Switch to a different strategy class.
                         │
                         └── NO → Neutral Result
                                   The idea didn't help but wasn't harmful.
                                   Action: Revert. Log. Try a variation or move on.
```

### Parallels to Standard cliskill

| Research classification | Standard cliskill equivalent | Reasoning |
|---|---|---|
| Implementation Bug | Implementation Gap | Fix code, not hypothesis |
| Destructive Hypothesis | Spec Gap | The idea was wrong |
| Exhausted Direction | Non-convergence escalation | Switch strategy or escalate |
| Neutral Result | — | No direct parallel — standard cliskill has no "didn't help but didn't hurt" |

---

## Strategy Classes

Experiments are grouped into strategy classes, analogous to cliskill's failure grouping. The agent tracks which classes have been explored and their yield (keep rate).

### Standard Strategy Classes

| Class | Examples | Typical experiment count |
|---|---|---|
| **Hyperparameter tuning** | Learning rate, depth, regularization, batch size | 3–8 |
| **Feature selection** | Add, remove, reorder, transform features | 3–6 |
| **Architecture changes** | Model type, ensemble, two-stage, embedding dimension | 2–4 |
| **Data manipulation** | Training window, sample weights, augmentation, outlier handling | 2–5 |

### Tracking

For each strategy class, maintain:

```
class: {name}
experiments_run: {N}
experiments_kept: {M}
keep_rate: {M/N}
status: {active | exhausted | untried}
last_outcome: {keep | revert}
consecutive_reverts: {N}
```

### Exhaustion Rule

A strategy class is **exhausted** when:
- 3 or more consecutive experiments in that class were reverted, OR
- The keep rate drops below 0.2 after 5+ experiments

When a class is exhausted, switch to the next unexplored class. Do not return to an exhausted class unless the human explicitly requests it.

---

## Convergence Detection

Adapted from loop-protocol.md's convergence rules, extended for continuous metrics.

### The loop is converging if, in the last N experiments:

- At least 1 experiment was kept, OR
- The best-so-far metric improved

### The loop is NOT converging if:

- Last 5 experiments were all reverted, AND
- They span at least 2 different strategy classes

### Actions on Non-Convergence

```
1. Only 1 strategy class tried so far?
   ├── YES → Switch class, continue
   │
   └── NO → continue
              │
              2. 2+ classes exhausted?
              ├── YES but not ALL → Switch to untried class, continue
              │
              └── ALL classes exhausted → Escalate
                    │
                    Present to human:
                    "Metric may be saturated. Options:
                     (A) Refine metric definition
                     (B) Expand editable surface (new features, new data)
                     (C) Accept current best"
```

---

## State Tracking

Extends `.cliskill/state.md` format for research mode.

### Research State Format

```markdown
# cliskill Pipeline State

mode: research
phase: {DISCOVER | NEGOTIATE | BOOTSTRAP | OPTIMIZE | REVIEW}
status: {in_progress | pending_review | stalled | complete}
metric_name: {name from metric definition}
metric_score_best: {best score achieved so far}
metric_score_baseline: {first experiment score}
experiment_count: {total experiments run}
kept_count: {experiments kept}
current_strategy_class: {hyperparameter | feature | architecture | data}
exhausted_classes: [{comma-separated}]
last_5_outcomes: [{keep, revert, revert, keep, revert}]
started: {ISO 8601 timestamp}
last_updated: {ISO 8601 timestamp}
```

### Primary Artifacts

- **`results.tsv`** is the primary artifact (analogous to `loop-N/eval-report.md`). Append-only log of every experiment.
- Each experiment is a **git commit**. State is always recoverable via `git log` and `git reset`.

---

## The Research Pipeline

Maps to cliskill's existing phases:

| cliskill phase | Research equivalent | What happens |
|---|---|---|
| DISCOVER | **DISCOVER** | Cross-reference data/code capabilities with domain knowledge (existing `references/discovery-protocol.md`) |
| SPECIFY | **NEGOTIATE** | Metric-compiler conversation: 5 scenario questions → 2 candidate metrics → human picks |
| BUILD | **BOOTSTRAP** | Generate `program.md` + `metric.py` + `eval_harness.py`. Dry-run 2–3 experiments to verify loop works |
| VERIFY | **OPTIMIZE** | The autoresearch loop — PROPOSE → RUN → CLASSIFY → KEEP/REVERT. Runs until convergence stalls |
| REPAIR | *(integrated)* | Failure classification is per-experiment, not per-loop. Bugs get fixed inline, bad ideas get logged |
| DEPLOY | **REVIEW** | Present Pareto front to human. Guided walk-through of tradeoffs. Human picks winner or refines metric |

### Phase Transitions

```
DISCOVER → NEGOTIATE → BOOTSTRAP → OPTIMIZE ←→ (per-experiment classify)
                                       ↓
                                    REVIEW
                                       ↓
                          (accept | refine metric → NEGOTIATE)
```

---

## Metric Verification

Before entering OPTIMIZE, verify the metric itself is sound. Analogous to cliskill's "holdout scenarios are sacred" — the metric ground truth is verified before the loop trusts it.

### Verification Steps

1. **Known-good cases.** Run the metric on inputs where the correct answer is known (e.g., known drought events should score high severity). The metric must rank these correctly.

2. **Known-bad cases.** Run the metric on inputs where the result should be clearly different (e.g., normal years should score low severity). The metric must not rank these the same as good cases.

3. **Sensitivity check.** Perturb a known-good input slightly. The metric should change proportionally, not wildly or not at all.

### On Failure

If the metric ranks known cases wrong:

```
STOP. Do not enter OPTIMIZE.
Escalate to human:
  "The metric does not correctly rank known cases.
   {case}: expected {X}, got {Y}.
   Fix the metric definition before running optimization."
```

Re-enter NEGOTIATE to refine the metric. Do not burn optimization loops on a broken metric.

---

## Guided Review

Adapted from cliskill's guided escalation. When OPTIMIZE stalls or completes a session, present results interactively.

### Review Format

```markdown
## cliskill — Research Review

### Best Result
Best model so far: commit {hash} (score {Y}).
Baseline was {Z}. Improvement: {W}%.

### Strategy Summary

| Strategy Class | Experiments | Kept | Keep Rate | Status |
|---|---|---|---|---|
| Hyperparameter tuning | 10 | 4 | 40% | exhausted |
| Feature selection | 8 | 2 | 25% | exhausted |
| Architecture changes | 3 | 0 | 0% | exhausted |
| Data manipulation | — | — | — | untried |

### Top Tradeoff Options (Pareto Front)

| # | Commit | Primary Metric | Secondary Metric | Notes |
|---|--------|---------------|-----------------|-------|
| 1 | {hash} | {score} | {score} | Best primary |
| 2 | {hash} | {score} | {score} | Best secondary |
| 3 | {hash} | {score} | {score} | Balanced |

### Recommendations

1. **Continue optimizing** — {estimated headroom based on recent trajectory}
2. **Refine metric** — {if many "neutral" results suggest the metric isn't sensitive enough}
3. **Accept current best and deploy** — {if improvement has plateaued}
```

### After Review

| Human choice | Action |
|---|---|
| Continue optimizing | Re-enter OPTIMIZE. Reset consecutive-revert counters. |
| Refine metric | Re-enter NEGOTIATE. Start a new session after metric is updated. |
| Accept current best | Checkout best commit. Produce final artifacts. Mark COMPLETE. |

---

## Loop Invariants

These must hold true throughout the research loop:

1. **Eval harness is read-only.** The optimization loop never modifies the evaluation function. To change how experiments are scored, exit OPTIMIZE and re-enter NEGOTIATE.

2. **`results.tsv` is append-only.** Never delete or modify previous experiment entries. Discarded experiments stay in the log — they map the boundaries of what doesn't work.

3. **Git is the checkpoint.** Every experiment is a commit. Reverts are `git reset`. State is always recoverable. If the process crashes, `git log` + `results.tsv` are sufficient to resume.

4. **Metric definition is immutable within a session.** To change the metric, exit OPTIMIZE, re-enter NEGOTIATE, and start a new session. Don't change the rules mid-game.

5. **Log everything, even failures.** Discarded experiments are as valuable as kept ones. Every experiment gets a `results.tsv` entry with its classification (kept, bug, destructive, exhausted, neutral).

---

## Relationship to Other Reference Files

### `evaluation-router.md`
Research protocol's experiment classification is a **parallel tree**, not a replacement. Software failures use Spec/Impl/Scenario Gap. Research failures use Bug/Destructive/Exhausted/Neutral. Both share the same structural principle: classify the failure type, then route to the correct action.

### `loop-protocol.md`
Research protocol extends convergence detection from per-scenario to per-strategy-class. State tracking adds metric-specific fields (`metric_score_best`, `experiment_count`, `exhausted_classes`). The core invariant is the same: state is always written before action, and previous artifacts are immutable.

### `discovery-protocol.md`
Discovery feeds directly into the DISCOVER phase of research. The ranked capability list becomes the starting point for strategy class selection. If discovery found that the repo has strong data pipelines but limited model variety, the agent should prioritize data manipulation strategies over architecture changes.

---

## Status Lines

```
cliskill ▸ RESEARCH ▸ negotiate    5 scenario questions → candidate metrics
cliskill ▸ RESEARCH ▸ negotiate    Metric selected: {name}
cliskill ▸ RESEARCH ▸ bootstrap    Generating program.md + metric.py + eval_harness.py
cliskill ▸ RESEARCH ▸ bootstrap    Dry-run {N} of 3...
cliskill ▸ RESEARCH ▸ bootstrap    Loop verified — entering OPTIMIZE
cliskill ▸ RESEARCH ▸ verify-metric Running known-case validation...
cliskill ▸ RESEARCH ▸ verify-metric {N}/{M} known cases ranked correctly
cliskill ▸ RESEARCH ▸ optimize     Experiment {N}: {1-line description}
cliskill ▸ RESEARCH ▸ optimize     Result: {keep | revert} — {metric_value} (best: {best})
cliskill ▸ RESEARCH ▸ optimize     Strategy class {name}: {kept}/{total} kept
cliskill ▸ RESEARCH ▸ optimize     Class {name} exhausted — switching to {next}
cliskill ▸ RESEARCH ▸ stalled      Last 5 experiments reverted across 2+ classes
cliskill ▸ RESEARCH ▸ review       Presenting results for human review
cliskill ▸ RESEARCH ▸ done         Best: {score} (baseline: {baseline}, improvement: {W}%)
```
