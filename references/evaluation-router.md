# Evaluation Router

Decision tree for classifying failures and routing automated actions in the cliskill repair loop.

---

## Classification Decision Tree

For each failed scenario in the evaluation report:

```
1. Is the expected behavior described in .clarity/spec.md?
   ├── NO → Spec Gap
   │        The spec didn't cover this case or was ambiguous.
   │        Action: Update spec, regenerate skill brief, rebuild.
   │
   └── YES → continue
              │
              2. Does the implementation match what the spec says?
              ├── NO → Implementation Gap
              │        The spec was clear but the code doesn't match.
              │        Action: Generate targeted fix prompt, rebuild.
              │
              └── YES → continue
                         │
                         3. Does the scenario accurately test what the spec says?
                         ├── NO → Scenario Gap
                         │        The holdout test itself is wrong.
                         │        Action: Escalate to human. Never auto-fix.
                         │
                         └── YES → Integration Issue
                                   Investigate deeper. May need human analysis.
                                   Action: Escalate with diagnostic context.
```

---

## Action Table

| Root Cause | Automated Action | What Changes | Loop Target |
|---|---|---|---|
| **Spec Gap** | Update spec requirement, regenerate skill-brief | `spec.md`, `skill-brief.md` | Phase 2 (BUILD) |
| **Implementation Gap** | Generate targeted fix prompt with failure context | Skill code only | Phase 2 (BUILD) with fix context |
| **Scenario Gap** | Escalate to human — holdout tests are sacred | Nothing | Exit loop |
| **Mixed (spec + impl)** | Fix spec first, impl gaps may self-resolve | `spec.md`, then skill code | Phase 2 (BUILD) |
| **Integration Issue** | Escalate with full diagnostic context | Nothing | Exit loop |

---

## Classification Conservatism

**When the root cause is ambiguous, default to Spec Gap.**

The classifier (the agent reading the eval report) can be wrong. The dangerous failure mode: a Spec Gap gets misclassified as an Implementation Gap. cliskill generates a targeted fix prompt, rebuilds, the same scenario fails again, burns another loop, fails again, then escalates after 3 iterations with a confusing diagnostic. The user has no idea the spec was wrong from the start.

The cost asymmetry is clear:
- **Unnecessary spec update** (Spec Gap when it was really Implementation Gap): costs one extra loop. The spec gets a harmless clarification, the rebuild fixes the real issue.
- **Missed spec gap** (Implementation Gap when it was really Spec Gap): costs all three loops plus a confusing escalation. The agent keeps patching code that has the wrong spec underneath it.

**Rule: When you cannot confidently determine whether the spec covers the failing behavior, classify as Spec Gap.** Only classify as Implementation Gap when the spec unambiguously describes the expected behavior and the code clearly diverges from it.

---

## Priority Rules for Mixed Failures

When an evaluation report contains multiple failure types:

1. **Spec Gaps take priority.** Always fix spec gaps before attempting implementation fixes. Rationale: a corrected spec often resolves implementation gaps as a side effect — the builder now has clearer instructions.

2. **Group related spec gaps.** If multiple failures point to the same missing or ambiguous requirement, fix the root requirement once rather than patching each failure individually.

3. **Implementation gaps get targeted fixes.** Don't re-architect. Provide specific, surgical guidance for each failing scenario.

4. **Scenario gaps are never auto-fixed.** Even if the fix seems obvious, escalate. The holdout separation exists precisely to prevent the builder from gaming its own tests.

---

## Spec Gap Fix Protocol

When updating the spec for a Spec Gap:

1. Identify the missing or ambiguous requirement.
2. Add or clarify the requirement in `.clarity/spec.md`, following the existing format (FR-NNN numbering).
3. Add a note in the requirement: `<!-- Added by cliskill loop {N} to address SC-{NNN} -->`.
4. Regenerate `.clarity/skill-brief.md` to reflect the spec change.
5. Record the diff in `.cliskill/loop-{N}/changes.md`.

---

## Rebuild Context Template

When rebuilding after **Implementation Gaps**, append this section to the skill brief before passing to `/agent-skill-creator`:

```markdown
## Rebuild Context (loop #{N})

Previous build failed the following scenarios. Apply targeted fixes only.
Do NOT re-architect. Preserve all passing behavior.

### Failures to fix

1. **SC-{NNN}: {scenario title}**
   - **Expected:** {expected behavior from scenario}
   - **Actual:** {actual behavior from eval report}
   - **Root cause:** Implementation Gap
   - **Fix guidance:** {specific, actionable fix description}

2. **SC-{NNN}: {scenario title}**
   - **Expected:** {expected behavior}
   - **Actual:** {actual behavior}
   - **Root cause:** Implementation Gap
   - **Fix guidance:** {specific fix description}

### Constraints
- Fix ONLY the listed failures.
- Do not modify behavior that passes existing scenarios.
- If a fix requires changing shared code, verify it doesn't break passing tests.
```

---

## Rebuild Context Template (Spec Gaps)

When rebuilding after **Spec Gap** fixes, the context is implicit — the updated skill brief already contains the corrected requirements. Add a note:

```markdown
## Rebuild Context (loop #{N})

Spec was updated to address gaps found in evaluation. Key changes:

- FR-{NNN}: {summary of what was added/clarified}
- FR-{NNN}: {summary of what was added/clarified}

Rebuild from the updated skill brief. The new requirements above are the
primary targets — ensure they are implemented correctly.
Previous passing behavior must be preserved.
```

---

## Convergence Detection

A failure is **not converging** if:

- The same scenario ID (SC-NNN) fails in two consecutive loops, AND
- The root cause classification is the same in both loops, AND
- The fix attempt was substantively different between loops (not just a retry of the same fix)

When non-convergence is detected, escalate immediately. Do not waste the third loop on a failure that isn't responding to automated fixes.

A failure **has shifted** (and is still worth pursuing) if:

- The scenario ID is the same but the root cause changed (e.g., Spec Gap → Implementation Gap), OR
- The actual behavior changed (the fix had partial effect)

Shifted failures get one more loop iteration before escalation.
