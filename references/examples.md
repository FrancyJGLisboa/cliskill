# cliskill Examples

Three complete examples showing the pipeline in action: a happy path, an implementation fix loop, and a spec fix loop.

---

## Example 1: Happy Path (No Repair Needed)

**Input:** User provides a GitHub repo URL for a weather API wrapper.

```
/cliskill https://github.com/example/weather-api docs/api-reference.pdf
```

### Phase 1: SPECIFY

```
cliskill ▸ SPECIFY ▸ starting    Delegating to /clarity with 2 reference(s)
cliskill ▸ SPECIFY ▸ INGEST      Reading weather-api repo...
cliskill ▸ SPECIFY ▸ INGEST      Reading api-reference.pdf...
cliskill ▸ SPECIFY ▸ INGEST      12 endpoints / 5 models extracted
cliskill ▸ SPECIFY ▸ SPECIFY     Generating spec...
cliskill ▸ SPECIFY ▸ SPECIFY     12 requirements drafted
cliskill ▸ SPECIFY ▸ SCENARIO    Creating holdout scenarios...
cliskill ▸ SPECIFY ▸ SCENARIO    8 scenarios created
cliskill ▸ SPECIFY ▸ HANDOFF     Generating skill brief...
cliskill ▸ SPECIFY ▸ done        Ready for review — 12 requirements, 8 scenarios
```

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

```
cliskill ▸ BUILD ▸ starting      Delegating to /agent-skill-creator
cliskill ▸ BUILD ▸ architecture  Designing skill structure...
cliskill ▸ BUILD ▸ detection     Detecting target platforms...
cliskill ▸ BUILD ▸ detection     Found: claude, gemini
cliskill ▸ BUILD ▸ implement     Building weather-api-skill...
cliskill ▸ BUILD ▸ validate      Running validation + security scan...
cliskill ▸ BUILD ▸ done          weather-api-skill built (7 files)
```

### Phase 3: VERIFY

```
cliskill ▸ VERIFY ▸ starting     Running 8 holdout scenarios...
cliskill ▸ VERIFY ▸ SC-001       ✓ Basic forecast retrieval
cliskill ▸ VERIFY ▸ SC-002       ✓ Multi-day forecast range
cliskill ▸ VERIFY ▸ SC-003       ✓ Invalid location handling
cliskill ▸ VERIFY ▸ SC-004       ✓ Unit conversion (metric/imperial)
cliskill ▸ VERIFY ▸ SC-005       ✓ API rate limit response
cliskill ▸ VERIFY ▸ SC-006       ✓ Missing API key error
cliskill ▸ VERIFY ▸ SC-007       ✓ Historical weather query
cliskill ▸ VERIFY ▸ SC-008       ✓ Concurrent location batch
cliskill ▸ VERIFY ▸ done         8/8 passed
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

User approves.

```
cliskill ▸ DEPLOY ▸ starting     Installing to 2 platform(s)...
cliskill ▸ DEPLOY ▸ installed    claude ✓
cliskill ▸ DEPLOY ▸ installed    gemini ✓
cliskill ▸ DEPLOY ▸ done         Deployed to claude, gemini
```

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

```
cliskill ▸ SPECIFY ▸ starting    Delegating to /clarity with 2 reference(s)
cliskill ▸ SPECIFY ▸ INGEST      Reading portfolio-spec.md...
cliskill ▸ SPECIFY ▸ INGEST      Reading finnhub.io/docs/api...
cliskill ▸ SPECIFY ▸ INGEST      23 endpoints / 8 models extracted
cliskill ▸ SPECIFY ▸ SPECIFY     15 requirements drafted
cliskill ▸ SPECIFY ▸ SCENARIO    10 scenarios created
cliskill ▸ SPECIFY ▸ HANDOFF     Generating skill brief...
cliskill ▸ SPECIFY ▸ done        Ready for review — 15 requirements, 10 scenarios
```

User approves.

### Phase 2: BUILD → complete

```
cliskill ▸ BUILD ▸ starting      Delegating to /agent-skill-creator
cliskill ▸ BUILD ▸ architecture  Designing skill structure...
cliskill ▸ BUILD ▸ detection     Found: claude
cliskill ▸ BUILD ▸ implement     Building portfolio-tracker-skill...
cliskill ▸ BUILD ▸ validate      Running validation + security scan...
cliskill ▸ BUILD ▸ done          portfolio-tracker-skill built (8 files)
```

### Phase 3: VERIFY → 2 failures

```
cliskill ▸ VERIFY ▸ starting     Running 10 holdout scenarios...
cliskill ▸ VERIFY ▸ SC-001       ✓ Basic portfolio summary
cliskill ▸ VERIFY ▸ SC-002       ✓ Add position
cliskill ▸ VERIFY ▸ SC-003       ✓ Remove position
cliskill ▸ VERIFY ▸ SC-004       ✗ Portfolio returns calculation — wrong formula
cliskill ▸ VERIFY ▸ SC-005       ✓ Empty portfolio handling
cliskill ▸ VERIFY ▸ SC-006       ✓ Invalid ticker error
cliskill ▸ VERIFY ▸ SC-007       ✗ Multi-currency display — no conversion
cliskill ▸ VERIFY ▸ SC-008       ✓ Historical performance
cliskill ▸ VERIFY ▸ SC-009       ✓ API key missing
cliskill ▸ VERIFY ▸ SC-010       ✓ Large portfolio (50+ positions)
cliskill ▸ VERIFY ▸ done         8/10 passed
```

### Repair Loop — Iteration 1

```
cliskill ▸ REPAIR ▸ loop 1       2 failure(s) to fix
cliskill ▸ REPAIR ▸ classify     SC-004: Implementation Gap
cliskill ▸ REPAIR ▸ classify     SC-007: Implementation Gap
cliskill ▸ REPAIR ▸ fix-impl     Generating rebuild context for 2 failure(s)...
cliskill ▸ REPAIR ▸ rebuilding   Back to BUILD (loop 1 of 3)
```

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

### Phase 2 (rebuild): BUILD

```
cliskill ▸ BUILD ▸ starting      Delegating to /agent-skill-creator (rebuild)
cliskill ▸ BUILD ▸ implement     Rebuilding portfolio-tracker-skill with fix context...
cliskill ▸ BUILD ▸ validate      Running validation + security scan...
cliskill ▸ BUILD ▸ done          portfolio-tracker-skill rebuilt (8 files)
```

### Phase 3 (re-verify): VERIFY → all pass

```
cliskill ▸ VERIFY ▸ starting     Running 10 holdout scenarios...
cliskill ▸ VERIFY ▸ SC-004       ✓ Portfolio returns calculation (was ✗)
cliskill ▸ VERIFY ▸ SC-007       ✓ Multi-currency display (was ✗)
cliskill ▸ VERIFY ▸ done         10/10 passed
```

### Phase 4: DEPLOY → approved and deployed

```
cliskill ▸ DEPLOY ▸ starting     Installing to 1 platform(s)...
cliskill ▸ DEPLOY ▸ installed    claude ✓
cliskill ▸ DEPLOY ▸ done         Deployed to claude
```

**Total loops: 1**

---

## Example 3: Spec Fix Loop

**Input:** User provides a Notion API integration concept.

```
/cliskill https://developers.notion.com/reference "I want a skill that syncs
Notion databases to local markdown files, with bidirectional conflict resolution"
```

### Phase 1: SPECIFY → approved

```
cliskill ▸ SPECIFY ▸ starting    Delegating to /clarity with 2 reference(s)
cliskill ▸ SPECIFY ▸ INGEST      Reading developers.notion.com/reference...
cliskill ▸ SPECIFY ▸ INGEST      34 endpoints / 12 models extracted
cliskill ▸ SPECIFY ▸ SPECIFY     18 requirements drafted
cliskill ▸ SPECIFY ▸ SCENARIO    12 scenarios created
cliskill ▸ SPECIFY ▸ HANDOFF     Generating skill brief...
cliskill ▸ SPECIFY ▸ done        Ready for review — 18 requirements, 12 scenarios
```

User approves.

### Phase 2: BUILD → complete

```
cliskill ▸ BUILD ▸ starting      Delegating to /agent-skill-creator
cliskill ▸ BUILD ▸ architecture  Designing skill structure...
cliskill ▸ BUILD ▸ detection     Found: claude
cliskill ▸ BUILD ▸ implement     Building notion-sync-skill...
cliskill ▸ BUILD ▸ validate      Running validation + security scan...
cliskill ▸ BUILD ▸ done          notion-sync-skill built (11 files)
```

### Phase 3: VERIFY → 3 failures

```
cliskill ▸ VERIFY ▸ starting     Running 12 holdout scenarios...
cliskill ▸ VERIFY ▸ SC-001       ✓ Basic page sync
cliskill ▸ VERIFY ▸ SC-002       ✓ New local page push
cliskill ▸ VERIFY ▸ SC-003       ✗ Conflict with both sides modified — no merge strategy
cliskill ▸ VERIFY ▸ SC-004       ✓ Property type mapping
cliskill ▸ VERIFY ▸ SC-005       ✓ Auth token expired
cliskill ▸ VERIFY ▸ SC-006       ✓ Database schema change
cliskill ▸ VERIFY ▸ SC-007       ✓ Offline resilience
cliskill ▸ VERIFY ▸ SC-008       ✗ Sync with nested databases — only top-level
cliskill ▸ VERIFY ▸ SC-009       ✓ Markdown frontmatter round-trip
cliskill ▸ VERIFY ▸ SC-010       ✓ Sync with deleted pages
cliskill ▸ VERIFY ▸ SC-011       ✗ Large database pagination — first page only
cliskill ▸ VERIFY ▸ SC-012       ✓ Concurrent sync conflict
cliskill ▸ VERIFY ▸ done         9/12 passed
```

### Repair Loop — Iteration 1

```
cliskill ▸ REPAIR ▸ loop 1       3 failure(s) to fix
cliskill ▸ REPAIR ▸ classify     SC-003: Spec Gap
cliskill ▸ REPAIR ▸ classify     SC-008: Spec Gap
cliskill ▸ REPAIR ▸ classify     SC-011: Implementation Gap
cliskill ▸ REPAIR ▸ fix-spec     Updating 2 requirement(s) in spec...
cliskill ▸ REPAIR ▸ rebuilding   Back to BUILD (loop 1 of 3)
```

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

### Phase 2 (rebuild): BUILD

```
cliskill ▸ BUILD ▸ starting      Delegating to /agent-skill-creator (rebuild)
cliskill ▸ BUILD ▸ implement     Rebuilding notion-sync-skill with spec updates...
cliskill ▸ BUILD ▸ validate      Running validation + security scan...
cliskill ▸ BUILD ▸ done          notion-sync-skill rebuilt (11 files)
```

### Phase 3 (re-verify): VERIFY → 1 failure

```
cliskill ▸ VERIFY ▸ starting     Running 12 holdout scenarios...
cliskill ▸ VERIFY ▸ SC-003       ✓ Conflict with both sides modified (was ✗)
cliskill ▸ VERIFY ▸ SC-008       ✓ Sync with nested databases (was ✗)
cliskill ▸ VERIFY ▸ SC-010       ✗ Sync with deleted pages — stale local files
cliskill ▸ VERIFY ▸ SC-011       ✓ Large database pagination (was ✗)
cliskill ▸ VERIFY ▸ done         11/12 passed
```

### Repair Loop — Iteration 2

```
cliskill ▸ REPAIR ▸ loop 2       1 failure(s) to fix
cliskill ▸ REPAIR ▸ classify     SC-010: Implementation Gap
cliskill ▸ REPAIR ▸ fix-impl     Generating rebuild context for 1 failure(s)...
cliskill ▸ REPAIR ▸ rebuilding   Back to BUILD (loop 2 of 3)
```

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

### Phase 2 (rebuild): BUILD

```
cliskill ▸ BUILD ▸ starting      Delegating to /agent-skill-creator (rebuild)
cliskill ▸ BUILD ▸ implement     Rebuilding notion-sync-skill with fix context...
cliskill ▸ BUILD ▸ validate      Running validation + security scan...
cliskill ▸ BUILD ▸ done          notion-sync-skill rebuilt (11 files)
```

### Phase 3 (re-verify): VERIFY → all pass

```
cliskill ▸ VERIFY ▸ starting     Running 12 holdout scenarios...
cliskill ▸ VERIFY ▸ SC-010       ✓ Sync with deleted pages (was ✗)
cliskill ▸ VERIFY ▸ done         12/12 passed
```

### Phase 4: DEPLOY → approved and deployed

```
cliskill ▸ DEPLOY ▸ starting     Installing to 1 platform(s)...
cliskill ▸ DEPLOY ▸ installed    claude ✓
cliskill ▸ DEPLOY ▸ done         Deployed to claude
```

```
cliskill — Complete

✓ Specified: 20 requirements (18 original + 2 added in loop), 12 holdout scenarios
✓ Built: notion-sync-skill (11 files)
✓ Verified: 12/12 scenarios passed (2 repair loops)
✓ Deployed to: claude
```

**Total loops: 2** (1 spec fix + 1 implementation fix)

---

## Example 4: Update Mode

**Input:** The weather API from Example 1 has released v2 with new endpoints and a breaking change.

```
/cliskill update ./weather-api-skill https://api.example.com/docs/v2
```

### Phase 0: UPDATE

```
cliskill ▸ UPDATE ▸ starting     Reading existing skill at ./weather-api-skill
cliskill ▸ UPDATE ▸ existing     Found: 12 requirements, 8 scenarios
cliskill ▸ UPDATE ▸ INGEST       Reading api.example.com/docs/v2...
cliskill ▸ UPDATE ▸ diffing      Comparing new references against existing spec...
```

**Update Plan:**
```
cliskill — Update Plan

Existing skill: weather-api-skill
Current spec: 12 requirements, 8 scenarios

Changes detected

| # | Type | Description |
|---|------|-------------|
| 1 | New capability | POST /v2/batch-forecast — batch multiple locations |
| 2 | New capability | GET /v2/air-quality — AQI data |
| 3 | Changed behavior | GET /forecast now requires `units` param (was optional, defaulted to metric) |
| 4 | Deprecated | GET /forecast/legacy removed in v2 |

What will happen

- 2 new requirement(s) will be added to the spec
- 1 existing requirement(s) will be updated
- 1 requirement(s) will be marked deprecated
- 3 new holdout scenario(s) will be created
- All 8 existing scenarios will be re-run to catch regressions

Options: Approve / Select / Cancel
```

User approves.

```
cliskill ▸ UPDATE ▸ spec         Adding FR-013, FR-014; updating FR-004; deprecating FR-007
cliskill ▸ UPDATE ▸ scenarios    Creating SC-009, SC-010, SC-011
cliskill ▸ UPDATE ▸ done         Spec updated: 14 active requirements, 11 scenarios
```

### Phase 2: BUILD

```
cliskill ▸ BUILD ▸ starting      Delegating to /agent-skill-creator (update rebuild)
cliskill ▸ BUILD ▸ implement     Rebuilding weather-api-skill...
cliskill ▸ BUILD ▸ validate      Running validation + security scan...
cliskill ▸ BUILD ▸ done          weather-api-skill rebuilt (9 files)
```

### Phase 3: VERIFY

```
cliskill ▸ VERIFY ▸ starting     Running 11 scenarios (8 existing + 3 new)...
cliskill ▸ VERIFY ▸ SC-001       ✓ Basic forecast retrieval (existing)
cliskill ▸ VERIFY ▸ SC-002       ✓ Multi-day forecast range (existing)
cliskill ▸ VERIFY ▸ SC-003       ✓ Invalid location handling (existing)
cliskill ▸ VERIFY ▸ SC-004       ✗ Unit conversion (existing, regression) — units param now required
cliskill ▸ VERIFY ▸ SC-005       ✓ API rate limit response (existing)
cliskill ▸ VERIFY ▸ SC-006       ✓ Missing API key error (existing)
cliskill ▸ VERIFY ▸ SC-007       ✓ Historical weather query (existing)
cliskill ▸ VERIFY ▸ SC-008       ✓ Concurrent location batch (existing)
cliskill ▸ VERIFY ▸ SC-009       ✓ Batch forecast (new)
cliskill ▸ VERIFY ▸ SC-010       ✓ Air quality index (new)
cliskill ▸ VERIFY ▸ SC-011       ✗ Units parameter required (new) — still sending without units
cliskill ▸ VERIFY ▸ done         9/11 passed
```

### Repair Loop — Iteration 1

```
cliskill ▸ REPAIR ▸ loop 1       2 failure(s) to fix
cliskill ▸ REPAIR ▸ classify     SC-004: Implementation Gap (regression)
cliskill ▸ REPAIR ▸ classify     SC-011: Implementation Gap
cliskill ▸ REPAIR ▸ fix-impl     Generating rebuild context for 2 failure(s)...
cliskill ▸ REPAIR ▸ rebuilding   Back to BUILD (loop 1 of 3)
```

### Phase 2 (rebuild) → Phase 3 (re-verify) → all pass

```
cliskill ▸ VERIFY ▸ starting     Running 11 holdout scenarios...
cliskill ▸ VERIFY ▸ SC-004       ✓ Unit conversion (was ✗, regression fixed)
cliskill ▸ VERIFY ▸ SC-011       ✓ Units parameter required (was ✗)
cliskill ▸ VERIFY ▸ done         11/11 passed
```

### Phase 4: DEPLOY

```
cliskill ▸ DEPLOY ▸ starting     Installing to 2 platform(s)...
cliskill ▸ DEPLOY ▸ installed    claude ✓
cliskill ▸ DEPLOY ▸ installed    gemini ✓
cliskill ▸ DEPLOY ▸ done         Deployed to claude, gemini
```

```
cliskill — Complete (update)

✓ Updated: 14 active requirements (12 original, +2 new, -1 deprecated), 11 scenarios
✓ Built: weather-api-skill (9 files)
✓ Verified: 11/11 scenarios passed (1 repair loop)
✓ Deployed to: claude, gemini
```

**Total loops: 1**

---

## Example 5: Guided Escalation (Scenario Gap)

In Example 3, imagine if SC-003 had been classified as a Scenario Gap — the test was wrong, not the spec or implementation. Instead of dumping diagnostics, cliskill walks the user through it:

```
cliskill ▸ ESCALATE ▸ starting   1 failure(s) need your input
cliskill ▸ ESCALATE ▸ SC-003     Waiting for input...
```

```
cliskill — Needs Your Input (1/1 failures)

Loop: 1 of 3 | Reason: scenario_gap

SC-003: Conflict with both sides modified

What I expected: Merge both changes using field-level resolution
What happened: Last-write-wins applied
My classification: Scenario Gap
Why I think so: The spec (FR-012) explicitly says "use last-write-wins
for conflict resolution." The scenario expects field-level merge, which
contradicts the spec.

Options:
1. Agree with my classification — you edit SC-003, I'll re-verify
2. Reclassify — the spec should actually require field-level merge (Spec Gap)
3. Show me the code — see the conflict resolution implementation
4. Skip this one
```

**If the user picks option 1** (test is wrong):

The user edits `scenarios/SC-003.md` to expect last-write-wins instead of field-level merge.

```
cliskill ▸ ESCALATE ▸ SC-003     Resolved: Scenario Gap → user updated scenario
cliskill ▸ ESCALATE ▸ done       1 resolved — re-running verification
```

Then `/cliskill resume` re-runs all scenarios.

**If the user picks option 2** (spec should change):

```
cliskill ▸ ESCALATE ▸ SC-003     Resolved: Reclassified as Spec Gap → updating spec
cliskill ▸ ESCALATE ▸ done       1 resolved — rebuilding with spec fix
```

cliskill updates the spec to require field-level merge, regenerates the brief, and re-enters BUILD.

This is the holdout separation principle in action — the builder (cliskill + agent-skill-creator) never touches the tests. But instead of leaving the user alone with a diagnostic dump, it guides them to a decision.
