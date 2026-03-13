# cliskill Examples

Three complete examples showing the pipeline in action: a happy path, an implementation fix loop, and a spec fix loop.

---

## Example 1: Happy Path (No Repair Needed)

**Input:** User provides a GitHub repo URL for a weather API wrapper.

```
/cliskill https://github.com/example/weather-api docs/api-reference.pdf
```

### Phase 1: SPECIFY

cliskill delegates to `/clarity`:
- **INGEST**: Reads the repo, extracts API endpoints, auth patterns, data models → `.clarity/context.md`
- **SPECIFY**: Generates spec with 12 functional requirements (FR-001 through FR-012) → `.clarity/spec.md`
- **SCENARIO**: Creates 8 holdout scenarios (SC-001 through SC-008) → `scenarios/`
- **HANDOFF**: Produces skill brief with 4 priority analyses → `.clarity/skill-brief.md`

**Review Gate 1:**
```
cliskill — Specification Review

Clarity has produced:
- Spec: .clarity/spec.md (12 requirements)
- Scenarios: 8 holdout scenarios in scenarios/
- Skill Brief: .clarity/skill-brief.md

Options: Approve / Redirect / Adjust
```

User reviews and approves.

### Phase 2: BUILD

cliskill passes `.clarity/skill-brief.md` to `/agent-skill-creator`:
- Skips Discovery and Design (brief covers these)
- Creates skill directory with SKILL.md, scripts, references
- Validation passes, security scan clean

### Phase 3: VERIFY

cliskill runs `/clarity evaluate` against all 8 holdout scenarios:
```
Summary: 8/8 passed (100%)
```

No repair needed → proceed to Phase 4.

### Phase 4: DEPLOY

**Review Gate 2:**
```
cliskill — Deployment Review

Skill verified against 8 holdout scenarios. All passed.

Built skill: weather-api-skill
Options: Deploy / Review first / Skip deployment
```

User approves. Skill installed to Claude Code and Gemini CLI.

```
cliskill — Complete

✓ Specified: 12 requirements, 8 holdout scenarios
✓ Built: weather-api-skill (7 files)
✓ Verified: 8/8 scenarios passed
✓ Deployed to: claude, gemini
```

**Total loops: 0**

---

## Example 2: Implementation Fix Loop

**Input:** User provides docs for a stock portfolio tracker.

```
/cliskill ./docs/portfolio-spec.md https://finnhub.io/docs/api
```

### Phase 1: SPECIFY → approved

Clarity produces 15 requirements, 10 scenarios. User approves.

### Phase 2: BUILD → complete

Agent-skill-creator builds `portfolio-tracker-skill`.

### Phase 3: VERIFY → 2 failures

Evaluation report:
```
Summary: 8/10 passed (80%), 2 failed (20%)

Failed:
  SC-004: "Portfolio returns calculation" — Implementation Gap
    Expected: Annualized return using time-weighted formula
    Actual: Simple percentage return (not annualized)

  SC-007: "Multi-currency display" — Implementation Gap
    Expected: Convert all values to user's base currency
    Actual: Shows raw values in original currencies
```

### Repair Loop — Iteration 1

**Classification:** Both failures are Implementation Gaps (spec clearly states annualized returns and base currency conversion).

**Rebuild context appended to skill brief:**
```markdown
## Rebuild Context (loop #1)

Previous build failed the following scenarios. Apply targeted fixes only.

1. SC-004: Portfolio returns calculation
   - Expected: Annualized return using time-weighted formula
   - Actual: Simple percentage return (not annualized)
   - Root cause: Implementation Gap
   - Fix guidance: Use time-weighted rate of return formula.
     Annualize using (1 + TWR)^(365/days) - 1.

2. SC-007: Multi-currency display
   - Expected: Convert all values to user's base currency
   - Actual: Shows raw values in original currencies
   - Fix guidance: Add currency conversion step before display.
     Use the exchange rate endpoint already in the API decision.
```

### Phase 2 (rebuild): BUILD → complete

Agent-skill-creator rebuilds with fix context.

### Phase 3 (re-verify): VERIFY → all pass

```
Summary: 10/10 passed (100%)
```

### Phase 4: DEPLOY → approved and deployed

**Total loops: 1**

---

## Example 3: Spec Fix Loop

**Input:** User provides a Notion API integration concept.

```
/cliskill https://developers.notion.com/reference "I want a skill that syncs
Notion databases to local markdown files, with bidirectional conflict resolution"
```

### Phase 1: SPECIFY → approved

Clarity produces 18 requirements, 12 scenarios. User approves.

### Phase 2: BUILD → complete

Agent-skill-creator builds `notion-sync-skill`.

### Phase 3: VERIFY → 3 failures

```
Summary: 9/12 passed (75%), 3 failed (25%)

Failed:
  SC-003: "Conflict with both sides modified" — Spec Gap
    Expected: Merge both changes using field-level resolution
    Actual: Last-write-wins (spec didn't define merge strategy)

  SC-008: "Sync with nested databases" — Spec Gap
    Expected: Recursively sync child databases
    Actual: Only syncs top-level (spec didn't mention nesting)

  SC-011: "Large database pagination" — Implementation Gap
    Expected: Handle databases with >100 pages
    Actual: Only fetches first page (100 items max)
```

### Repair Loop — Iteration 1

**Classification:** 2 Spec Gaps + 1 Implementation Gap. Per cliskill rules: fix spec gaps first.

**Spec changes:**
```
Added to .clarity/spec.md:

FR-019: Conflict resolution shall use field-level three-way merge.
  When both local and remote modify the same field, prefer the
  version with the later timestamp. When different fields are
  modified, merge both changes.
  <!-- Added by cliskill loop 1 to address SC-003 -->

FR-020: Sync shall recursively discover and sync child databases
  (nested databases linked via relation properties). Maximum
  nesting depth: 3 levels.
  <!-- Added by cliskill loop 1 to address SC-008 -->
```

Skill brief regenerated with new requirements. Implementation Gap (SC-011) not explicitly targeted — may self-resolve with rebuild.

### Phase 2 (rebuild): BUILD → complete

Agent-skill-creator rebuilds from updated brief.

### Phase 3 (re-verify): VERIFY → 1 failure

```
Summary: 11/12 passed (91.7%), 1 failed (8.3%)

Passed (previously failing):
  SC-003: ✓ (spec gap fixed)
  SC-008: ✓ (spec gap fixed)
  SC-011: ✓ (self-resolved with rebuild — pagination now handled)

Failed (new):
  SC-010: "Sync with deleted pages" — Implementation Gap
    Expected: Detect remote deletions and remove local files
    Actual: Deleted pages remain as stale local files
```

### Repair Loop — Iteration 2

**Classification:** 1 Implementation Gap (new failure, not a regression — SC-010 wasn't failing before because a prerequisite feature wasn't working).

**Rebuild context:**
```markdown
## Rebuild Context (loop #2)

1. SC-010: Sync with deleted pages
   - Expected: Detect remote deletions and remove local files
   - Actual: Deleted pages remain as stale local files
   - Root cause: Implementation Gap
   - Fix guidance: Compare local file list against remote page IDs.
     Pages present locally but absent remotely should be moved to
     a .notion-sync/trash/ directory (soft delete).
```

### Phase 2 (rebuild): BUILD → complete
### Phase 3 (re-verify): VERIFY → all pass

```
Summary: 12/12 passed (100%)
```

### Phase 4: DEPLOY → approved and deployed

```
cliskill — Complete

✓ Specified: 20 requirements (18 original + 2 added in loop), 12 holdout scenarios
✓ Built: notion-sync-skill (11 files)
✓ Verified: 12/12 scenarios passed (2 repair loops)
✓ Deployed to: claude
```

**Total loops: 2** (1 spec fix + 1 implementation fix)

---

## Anti-Example: Scenario Gap Escalation

In Example 3, imagine if SC-003 had been classified as a Scenario Gap instead — the test was wrong, not the spec or implementation. cliskill would:

1. NOT auto-fix the scenario.
2. Escalate to the human:
   ```
   cliskill — Escalation

   Reason: scenario_gap
   All failures are Scenario Gaps. Holdout tests may need updating.

   Failures requiring attention:
     SC-003: "Conflict with both sides modified"
     Root cause: Scenario expected field-level merge but the spec
     intentionally uses last-write-wins for simplicity.

   After reviewing and adjusting scenarios, run /cliskill resume.
   ```
3. Wait for the human to fix the scenario, then resume.

This is the holdout separation principle in action — the builder (cliskill + agent-skill-creator) never touches the tests.
