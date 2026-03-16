# Self-Improvement Protocol

Two layers of continuous improvement: cliskill improves itself across builds, and every skill it produces ships ready to self-optimize post-deployment.

---

## §1 What Self-Improvement Solves

cliskill already produces verified skills. But two things are static:

1. **cliskill's own instructions** — SKILL.md, evaluation-router.md, loop-protocol.md never evolve based on build outcomes.
2. **Produced skills** — once deployed, a skill never gets better unless the user runs `/cliskill update`.

Self-improvement closes both loops.

| Mode | Target | Terminates when |
|------|--------|----------------|
| Standard | Binary pass/fail | All scenarios pass or 3 loops exhausted |
| Research | Continuous metric | Convergence stalls or human accepts |
| **Self-Improvement** | cliskill's own build efficiency | Always running — improves across builds |
| **Skill Optimization** | Per-skill quality post-deployment | User stops or convergence stalls |

---

## §2 Layer 1: cliskill Self-Improvement

### The Problem

cliskill doesn't know whether it's getting better or worse at building skills. Each build ends with an outcome — first-pass success, repair loops needed, escalation — but that data scatters into per-skill `.cliskill/` directories and is never aggregated.

### Metrics

Three metrics, computed from build outcomes:

| Metric | Definition | Source |
|--------|-----------|--------|
| `first_pass_rate` | Fraction of builds where all scenarios passed on the first VERIFY (loop_count = 0) | results.tsv |
| `avg_repair_loops` | Mean loop_count across all builds | results.tsv |
| `escalation_rate` | Fraction of builds that terminated via escalation (any reason) | results.tsv |

### Data Collection

**At the end of every DEPLOY or terminal escalation**, append a row to `~/acc/cliskill/.cliskill-meta/results.tsv`:

```
date	skill_name	mode	scenario_count	loop_count	first_pass	escalated	escalation_reason	notes
```

**Field definitions:**

| Field | Type | Description |
|-------|------|-------------|
| `date` | ISO 8601 date | Build completion date |
| `skill_name` | string | Name of the skill built |
| `mode` | enum | `standard`, `discover`, `research`, `update` |
| `scenario_count` | integer | Total holdout scenarios |
| `loop_count` | integer | Final loop count (0 = first-pass success) |
| `first_pass` | boolean | `true` if loop_count = 0 |
| `escalated` | boolean | `true` if build ended in escalation |
| `escalation_reason` | string | `scenario_gap`, `no_convergence`, `max_loops`, or empty |
| `notes` | string | Free-text — failure patterns, unusual conditions |

**Bootstrapping:** The first time cliskill appends a row, create the file with a header line if it doesn't exist. No data exists on day one — the loop cannot trigger until 5 rows accumulate.

### The Editable Surface (what CAN change)

| File | Why it's editable |
|------|------------------|
| `SKILL.md` | BUILD instructions, phase routing, status lines |
| `references/evaluation-router.md` | Classification heuristics, priority rules |
| `references/loop-protocol.md` | Convergence rules, partial progress handling |
| `references/examples.md` | Pattern references that guide the agent |

### The Eval Harness (what CANNOT change)

| File / artifact | Why it's sacred |
|-----------------|----------------|
| `references/self-improvement-protocol.md` | This file — the rules of self-improvement |
| Metric definitions (§2 table above) | Changing the metric invalidates all history |
| `results.tsv` format | Append-only, schema-fixed |
| Holdout-scenarios-are-sacred principle | Core invariant — no experiment can weaken it |

### The Loop

**Trigger:** After every 5th build (results.tsv row count mod 5 = 0), or manually via `/cliskill self-improve`.

**Steps:**

```
1. READ metrics
   - Load results.tsv
   - Compute first_pass_rate, avg_repair_loops, escalation_rate
   - Compare against previous snapshot (.cliskill-meta/metrics-snapshot.md)

2. IDENTIFY weakest metric
   - Use decision tree (below)
   - If all metrics are above threshold, report "no action needed" and stop

3. HYPOTHESIZE change
   - Read the editable file most likely to affect the weak metric
   - Propose a specific, targeted change
   - Write hypothesis to .cliskill-meta/current-experiment.md

4. PRESENT to user
   - Show: current metrics, weakest metric, hypothesis, proposed change
   - User approves, modifies, or rejects

5. APPLY change
   - Edit the target file
   - Commit with message: "self-improve: {hypothesis summary}"

6. MEASURE over next N builds
   - Next 5 builds accumulate naturally
   - After 5 builds, compare metrics against pre-experiment snapshot

7. CLASSIFY result
   - KEEP: target metric improved, no other metric worse by >10% absolute
   - REVERT: target metric did not improve, OR any metric worse by >10%
   - INCONCLUSIVE: <5 builds since experiment started — wait

8. Record outcome
   - Append to .cliskill-meta/experiments.tsv
   - Update metrics-snapshot.md
   - Clear current-experiment.md
```

### Decision Tree: Routing by Weakest Metric

```
if first_pass_rate < 0.6:
    → Target: SKILL.md (BUILD instructions, spec quality guidance)
    → Hypothesis class: "Improve how cliskill communicates requirements to /clarity
      or how it structures the skill brief for /agent-skill-creator"

else if avg_repair_loops > 1.5:
    → Target: evaluation-router.md (classification heuristics)
    → Hypothesis class: "Improve failure classification accuracy so the right
      fix is applied on the first repair attempt"

else if escalation_rate > 0.3:
    → Target: loop-protocol.md (convergence rules, edge case handling)
    → Hypothesis class: "Improve handling of edge cases that currently require
      human intervention"

else:
    → All metrics above threshold — no action needed
```

### Convergence Rules

- **One experiment at a time.** Never stack changes — you can't attribute improvement.
- **5 builds per experiment.** Minimum sample before classifying.
- **Destructive = any metric worse by >10% absolute.** Revert immediately, don't wait for 5 builds.
- **Revert = git revert.** The experiment commit is reverted, not manually undone.
- **No self-improvement during a user's build.** The loop triggers between builds, never during.

### State Files

```
~/acc/cliskill/.cliskill-meta/
├── results.tsv              # Build outcomes (append-only)
├── experiments.tsv           # Experiment log (append-only)
├── current-experiment.md     # Active experiment (empty if none)
└── metrics-snapshot.md       # Last computed metrics
```

**`experiments.tsv` format:**

```
date	experiment_id	target_file	hypothesis	builds_measured	result	metric_before	metric_after	commit_sha
```

**`current-experiment.md` format:**

```markdown
# Current Experiment

experiment_id: {E-NNN}
started: {ISO 8601}
target_file: {path}
target_metric: {metric name}
hypothesis: {what we're trying}
change_summary: {what was edited}
commit_sha: {sha}
builds_since: {N}
snapshot_before:
  first_pass_rate: {value}
  avg_repair_loops: {value}
  escalation_rate: {value}
```

**`metrics-snapshot.md` format:**

```markdown
# Metrics Snapshot

computed: {ISO 8601}
total_builds: {N}
window: all (or "last 20" once enough data exists)

first_pass_rate: {value}
avg_repair_loops: {value}
escalation_rate: {value}
```

---

## §3 Layer 2: Skills Ship with Eval Harness

Every skill produced by cliskill includes an `_optimize/` directory that enables post-deployment self-improvement using the autoresearch pattern.

### Directory Structure

```
{skill-name}/
├── SKILL.md              # existing
├── ...                   # existing skill files
└── _optimize/
    ├── program.md        # autoresearch instructions for this skill
    ├── eval.py           # evaluation harness (READ-ONLY post-deployment)
    ├── baseline.md       # initial build scores
    └── results.tsv       # experiment log (starts with baseline row)
```

### eval.py

Generated during BUILD from the holdout scenarios. Runs each scenario programmatically, computes `pass_rate` + optional `quality_score`. Fixed format output:

```json
{"pass_rate": 0.87, "quality_score": null, "scenarios": {"SC-001": "pass", "SC-002": "fail", ...}}
```

**Properties:**
- Generated once during BUILD from scenario definitions
- READ-ONLY after deployment — same principle as autoresearch's `prepare.py`
- If the metric needs to change, re-enter NEGOTIATE (research mode) or run `/cliskill update`
- Tests the skill's actual CLI interface — runs commands, checks output
- Does not require network access or API keys (uses recorded/mocked responses from scenarios)

### program.md

Template filled with skill-specific details during BUILD. Defines the optimization loop for this specific skill:

```markdown
# {skill-name} Optimization Program

## What Can Change (the editable surface)
- SKILL.md (prompt templates, argument parsing, output formatting)
- {skill-specific code files listed here}

## What Cannot Change (the eval harness)
- _optimize/eval.py
- _optimize/results.tsv format
- Holdout scenarios in scenarios/

## Metric
- Primary: pass_rate (fraction of scenarios passing)
- Secondary: quality_score (skill-specific, may be null)

## Strategy Classes
1. **Prompt refinement** — improve how the skill interprets user input
2. **Error handling** — improve graceful degradation for edge cases
3. **Output formatting** — improve JSON structure, field naming, completeness
4. **Argument parsing** — improve CLI argument validation and defaults

## The Loop
1. Run eval.py → record baseline
2. Pick strategy class with most room for improvement
3. Propose change → apply → run eval.py → classify
4. KEEP if pass_rate improved and no regression
5. REVERT if pass_rate dropped or quality_score degraded
6. Move to next strategy class when current one stalls (3 neutral in a row)

## Convergence
- Stop when all strategy classes exhausted
- Stop when pass_rate = 1.0 and quality_score stops improving
- Stop when user says stop
```

### baseline.md

Captured during VERIFY after all scenarios pass. Records the starting point for future optimization:

```markdown
# {skill-name} Optimization Baseline

captured: {ISO 8601}
cliskill_build_loops: {loop_count}

## Scores
pass_rate: {value}
quality_score: {value or null}

## Per-Scenario Results
| Scenario | Result | Notes |
|----------|--------|-------|
| SC-001 | pass | {timing, output quality note, etc.} |
| SC-002 | pass | |
| ... | ... | |
```

### results.tsv

Initialized with a baseline row during DEPLOY. Format:

```
commit	pass_rate	quality_score	strategy_class	status	description
```

**Status values:** `baseline`, `keep`, `revert`, `destructive`

The baseline row is written at deployment:

```
{sha}	{pass_rate}	{quality_score}	baseline	baseline	Initial build
```

---

## §4 Relationship Between Layers

Layer 2 feeds Layer 1. The connection is **advisory, not automatic:**

```
Multiple deployed skills discover same weakness
  (e.g., 3 skills needed error-handling fixes post-deployment)
    ↓
Pattern visible in Layer 2 results.tsv files across skills
    ↓
When /cliskill self-improve runs, it can reference these patterns
  as evidence for its Layer 1 hypothesis
    ↓
Layer 1 experiment targets the root cause in cliskill's BUILD instructions
  (e.g., "add explicit error-handling requirements to the skill brief template")
```

This is a human-in-the-loop connection. The agent running `/cliskill self-improve` may notice the pattern and propose it. No automation crosses the boundary.

---

## §5 Invariants

1. **results.tsv (both layers) is append-only.** Never delete or edit rows. Filter in queries, not in data.
2. **Self-improvement changes are always git-committed.** Revert = `git revert {sha}`, not manual undo. This preserves the experiment history.
3. **One experiment at a time.** No stacking — you cannot attribute improvement when multiple variables change.
4. **Holdout-scenarios-are-sacred is itself sacred.** No experiment — Layer 1 or Layer 2 — can weaken this principle. If an experiment's hypothesis involves changing how scenarios work, reject the hypothesis.
5. **Self-improvement never runs during a user's build.** Layer 1 triggers between builds. Layer 2 triggers when the user or an agent explicitly runs the optimization loop.
6. **eval.py is read-only post-deployment.** Changing the metric means re-entering NEGOTIATE (research mode) or running `/cliskill update`. This is the same principle as autoresearch's `prepare.py`.

---

## §6 Status Lines

### SELF-IMPROVE Mode

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

### BUILD Eval-Harness Generation

```
cliskill ▸ BUILD ▸ eval-harness   Generating _optimize/eval.py from {N} scenarios...
cliskill ▸ BUILD ▸ eval-harness   Generating _optimize/program.md...
cliskill ▸ BUILD ▸ eval-harness   Done — eval harness ready
```

### VERIFY Baseline Capture

```
cliskill ▸ VERIFY ▸ baseline      Running eval.py for optimization baseline...
cliskill ▸ VERIFY ▸ baseline      pass_rate: {v}, quality_score: {v}
cliskill ▸ VERIFY ▸ baseline      Baseline written to _optimize/baseline.md
```

### DEPLOY Metric Logging

```
cliskill ▸ DEPLOY ▸ metrics       Logging build outcome to .cliskill-meta/results.tsv
cliskill ▸ DEPLOY ▸ metrics       Build #{N}: {first_pass | loops: N | escalated}
```
