# Discovery Protocol

Rules for cliskill's DISCOVER mode: capability extraction, cross-referencing, feasibility analysis, and ranking.

---

## What Discovery Solves

Standard cliskill assumes the user knows what the skill should do — they provide API docs that describe endpoints, and clarity extracts a spec. Discovery mode handles the opposite case: the user has **sources of capability** (a repo, a library, a dataset) and **sources of knowledge** (course materials, textbooks, methodology docs) and wants to know **what's possible at the intersection**.

The output of discovery is not a spec — it's a **discovery report**: a ranked list of feasible capabilities that the user selects from before the spec is generated.

---

## Input Classification

Discovery takes two types of references:

### Capability sources
Things that **can do** or **contain data**:
- Git repositories (code, functions, pipelines, data models)
- Libraries or packages (installed or documented)
- Datasets or data schemas
- Running services or APIs

### Knowledge sources
Things that **teach methods** or **define what's valuable**:
- Course materials (PDFs, slides, textbooks)
- Methodology documentation
- Research papers
- Domain guides or best-practice documents

The agent must classify each reference as a capability source or knowledge source. When ambiguous (e.g., a repo that also contains tutorial notebooks), treat it as both.

---

## Discovery Phases

### Phase D1: Capability Extraction

Analyze each capability source to produce a structured inventory.

For **repositories**, extract:

| Category | What to find | Example |
|---|---|---|
| **Data structures** | Models, schemas, dataframes, tables | `PortfolioPosition`, `PriceTimeSeries`, `TradeLog` |
| **Functions/methods** | Public APIs, analysis functions, transforms | `calculate_returns()`, `optimize_portfolio()`, `backtest()` |
| **Data sources** | Connectors, imports, API clients | Finnhub client, CSV loader, database connection |
| **Pipelines** | End-to-end workflows already implemented | `ingest → clean → analyze → report` |
| **Dependencies** | Libraries that indicate capability | pandas, scipy, statsmodels, scikit-learn |

#### Guardrail: Evidence-Based Inventory (no inference from names)

Every capability claim MUST cite a specific source location. The agent must have **read the actual code**, not inferred from file names, README descriptions, or import statements.

| Claim type | Required evidence | NOT sufficient |
|---|---|---|
| "Function exists" | File path + line number + signature read from code | Seeing it in README or docstring |
| "Data structure has field X" | Class/schema definition read from code | Field name inferred from variable name |
| "Library is available" | Found in requirements.txt/pyproject.toml/package.json AND import works in code | Seeing `import X` in one file (could be unused/broken) |
| "Pipeline exists" | Traced the full flow: entry point → steps → output | Seeing a function named `run_pipeline()` |
| "Data source provides X" | Read the connector/client code, confirmed fields returned | API name mentioned in README |

Write the inventory to `.cliskill/discovery/capabilities.md`:

```markdown
# Capability Inventory

## Data Structures
- {name}: {description, fields, relationships}
  **Evidence:** {file_path}:{line_number} — {what was read}

## Functions
- {name}({params}): {what it does, return type}
  **Evidence:** {file_path}:{line_number} — {signature and logic confirmed}

## Data Sources
- {name}: {what data, format, freshness}
  **Evidence:** {file_path}:{line_number} — {connector/client code read}

## Existing Pipelines
- {name}: {steps, input → output}
  **Evidence:** {entry_point_file}:{line} → {step2_file}:{line} → ... → {output}

## Library Capabilities
- {library}: {what it enables that isn't directly in the code yet}
  **Evidence:** {requirements_file}:{line} — version {X.Y.Z}
```

**Anti-hallucination rule:** If the agent cannot provide a file path and line number for a capability claim, the claim must be downgraded to "unverified" and excluded from the cross-reference matrix. Unverified capabilities are listed separately and flagged in the discovery report.

### Phase D2: Knowledge Extraction

Analyze each knowledge source to produce a structured method catalog.

For **course materials / textbooks**, extract:

| Category | What to find | Example |
|---|---|---|
| **Methods/techniques** | Named analytics, algorithms, models | Sharpe ratio, Monte Carlo simulation, GARCH volatility |
| **Prerequisites** | What data/capabilities each method needs | "Requires: daily returns timeseries, risk-free rate" |
| **Outputs** | What each method produces | "Produces: risk-adjusted return score, confidence interval" |
| **Complexity** | Implementation difficulty | Simple formula vs. iterative optimization vs. ML model |
| **Value signal** | Why the course teaches it, how important it is | "Core concept" vs. "advanced topic" vs. "optional enrichment" |

Write the catalog to `.cliskill/discovery/knowledge.md`:

```markdown
# Knowledge Catalog

## Methods

### {Method Name}
- **Description:** {what it does}
- **Prerequisites:** {data types, functions, libraries needed}
- **Outputs:** {what it produces}
- **Complexity:** {simple | moderate | complex}
- **Importance:** {core | important | supplementary | advanced}
- **Source:** {course chapter/page, paper section}
```

### Phase D3: Cross-Reference Matrix

Match capabilities against knowledge to determine feasibility.

For each method in the knowledge catalog, check:

```
1. Does the capability inventory have the required data?
   ├── YES → data_ready
   ├── PARTIAL → data_gap (list what's missing)
   └── NO → data_blocked

2. Does the capability inventory have the required functions?
   ├── YES (exact match) → already_implemented
   ├── YES (partial) → needs_extension
   ├── NO (but libraries support it) → buildable
   └── NO (missing library + complex) → complex_build

3. Feasibility score:
   - already_implemented + data_ready = READY (just wire it up)
   - needs_extension + data_ready = LOW_EFFORT
   - buildable + data_ready = MODERATE_EFFORT
   - buildable + data_gap = HIGH_EFFORT
   - complex_build OR data_blocked = BLOCKED (note what's missing)
```

#### Guardrail: Feasibility Probes

Before finalizing the cross-reference matrix, run a **feasibility probe** for each method classified as READY or LOW_EFFORT. A probe is a minimal verification that the claimed capability actually works, not just exists.

**Probe types by claim:**

| Claim | Probe | Pass condition |
|---|---|---|
| `already_implemented` | Read the function body. Trace: does it actually compute what the method requires? | Logic matches the knowledge catalog's method description |
| `data_ready` | Read the data structure. Confirm all prerequisite fields exist with correct types. | Every field the method needs is present and typed correctly |
| `needs_extension` | Identify exactly what's missing. Is it a parameter? A wrapper? A new function? | Gap is articulable in one sentence, not vague |
| `buildable` | Confirm the library has the specific function/class needed. Read the library's import. | `from {library} import {specific_thing}` is valid |

**Probe results update the matrix:**

```
PROBE_PASS   → keep classification
PROBE_FAIL   → downgrade one level (READY → LOW_EFFORT, LOW → MODERATE, etc.)
PROBE_BLOCKED → reclassify as BLOCKED with specific reason
```

Write probe results to `.cliskill/discovery/probes.md`:

```markdown
# Feasibility Probes

## {Method Name}
- **Claim:** {original classification}
- **Probe:** {what was checked}
- **Result:** {PASS | FAIL | BLOCKED}
- **Evidence:** {file_path}:{line} — {what was found}
- **Final classification:** {updated classification}
```

**Anti-hallucination rule:** Any method classified as READY that fails its probe is automatically downgraded and flagged in the discovery report with the reason. The agent must NOT present a method as READY unless the probe passed.

#### Cross-Reference Matrix Format

Write the matrix to `.cliskill/discovery/cross-reference.md`:

```markdown
# Cross-Reference Matrix

| Method | Data | Functions | Feasibility | Effort | Probe | Notes |
|--------|------|-----------|-------------|--------|-------|-------|
| Sharpe Ratio | data_ready | already_implemented | READY | Wire up | PASS | `calculate_returns()` at analytics.py:42 |
| Monte Carlo | data_ready | buildable | MODERATE | Build | PASS | numpy.random confirmed in requirements |
| GARCH Volatility | data_ready | buildable | MODERATE | Build | PASS | statsmodels.tsa.api at requirements.txt:8 |
| Sentiment Analysis | data_blocked | complex_build | BLOCKED | — | N/A | No text data source |
```

### Phase D4: Ranking

Rank feasible methods by a composite score:

```
rank_score = importance_weight × feasibility_weight

importance_weight:
  core = 4, important = 3, supplementary = 2, advanced = 1

feasibility_weight:
  READY = 4, LOW_EFFORT = 3, MODERATE_EFFORT = 2, HIGH_EFFORT = 1, BLOCKED = 0
```

Sort descending. Group into tiers:

| Tier | Score Range | Meaning |
|------|-------------|---------|
| **Tier 1: Quick wins** | 12-16 | High importance + easy to build |
| **Tier 2: Worth building** | 6-11 | Good ROI, moderate effort |
| **Tier 3: Stretch goals** | 2-5 | Low importance or high effort |
| **Blocked** | 0 | Missing data or capabilities — note what's needed |

Write the ranked list to `.cliskill/discovery/ranked-analytics.md`.

---

## Discovery Report Format

The final discovery report presented to the user combines all phases:

```markdown
## cliskill — Discovery Report

**Capability sources analyzed:** {N} ({list})
**Knowledge sources analyzed:** {N} ({list})

### What this repo can do
{2-3 sentence summary of the repo's data and capabilities}

### What the reference material teaches
{2-3 sentence summary of the methods/analytics covered}

### Recommended Analytics (Tier 1 — quick wins)

| # | Analytics | Why | Effort | Based on |
|---|-----------|-----|--------|----------|
| 1 | {name} | {importance from course} | {READY/LOW} | {repo function + course method} |
| 2 | ... | | | |

### Worth Building (Tier 2)

| # | Analytics | Why | Effort | Based on |
|---|-----------|-----|--------|----------|
| 3 | {name} | {importance} | {MODERATE} | {what exists + what to build} |

### Stretch Goals (Tier 3)

| # | Analytics | Why | Effort | Gap |
|---|-----------|-----|--------|-----|
| 5 | {name} | {importance} | {HIGH} | {what's missing} |

### Blocked (not feasible without changes)

| # | Analytics | Blocker |
|---|-----------|---------|
| 7 | {name} | {missing data/capability} |

### Select analytics for the skill

Choose which analytics to include:
1. **All Tier 1 + Tier 2** (recommended)
2. **All Tier 1 only** (minimal viable skill)
3. **Custom selection** — pick specific analytics by number
4. **Everything feasible** (Tiers 1-3)
```

---

## Status Lines

```
cliskill ▸ DISCOVER ▸ starting     Analyzing {N} capability + {N} knowledge source(s)
cliskill ▸ DISCOVER ▸ capabilities Reading {source name}...
cliskill ▸ DISCOVER ▸ capabilities {N} data structures, {N} functions, {N} pipelines found
cliskill ▸ DISCOVER ▸ knowledge    Reading {source name}...
cliskill ▸ DISCOVER ▸ knowledge    {N} methods/techniques extracted
cliskill ▸ DISCOVER ▸ crossref     Matching capabilities against methods...
cliskill ▸ DISCOVER ▸ crossref     {N} feasible, {N} blocked
cliskill ▸ DISCOVER ▸ probes       Running feasibility probes on {N} candidates...
cliskill ▸ DISCOVER ▸ probes       {method}: {PASS | FAIL | BLOCKED} — {reason}
cliskill ▸ DISCOVER ▸ probes       {N} passed, {M} downgraded, {K} blocked
cliskill ▸ DISCOVER ▸ ranking      Scoring and ranking...
cliskill ▸ DISCOVER ▸ done         Discovery complete — {N} Tier 1, {N} Tier 2, {N} Tier 3, {N} blocked
```

---

## State Management

```
.cliskill/state.md:
  phase: DISCOVER
  status: {in_progress | pending_review}
  mode: discover
  capability_sources: [{list}]
  knowledge_sources: [{list}]

.cliskill/discovery/
├── capabilities.md        # Phase D1 output (with evidence citations)
├── knowledge.md           # Phase D2 output
├── cross-reference.md     # Phase D3 output (with probe results)
├── probes.md              # Feasibility probe results per method
└── ranked-analytics.md    # Phase D4 output + user selection
```

---

## From Discovery to SPECIFY

After the user selects analytics, the discovery artifacts feed into `/clarity` as structured input:

1. The selected analytics from `ranked-analytics.md` become the **scope** for the spec.
2. The capability inventory from `capabilities.md` tells clarity what already exists (don't re-invent).
3. The knowledge catalog from `knowledge.md` provides the method definitions clarity needs to write precise requirements.
4. The original references (repo, PDFs) are still available for clarity to consult.

The skill brief will include a `## Discovery Context` section that summarizes:
- Which analytics were selected and why
- What repo capabilities each analytics builds on
- What knowledge source defines the method

This context ensures agent-skill-creator builds on the repo's existing code rather than reimplementing from scratch.

---

## Feasibility Guardrails

Guardrails operate at four layers of the pipeline to ensure agents only suggest, specify, build, and ship analytics that actually work. Each layer catches different failure modes.

### Layer 1: Discovery-Time (prevent false feasibility claims)

These guardrails prevent the agent from claiming something is feasible when it isn't.

#### G1.1 — Evidence-Based Inventory (defined above in Phase D1)
Every capability claim requires a file path and line number. No inference from names, READMEs, or comments.

#### G1.2 — Feasibility Probes (defined above in Phase D3)
Every READY/LOW_EFFORT claim must pass a probe before being presented to the user. Failed probes downgrade the classification.

#### G1.3 — Explicit "Unverified" Category
If the agent cannot verify a capability but suspects it exists, it goes in a separate "Unverified" section — visible to the user but excluded from the cross-reference matrix and ranking. The discovery report flags these:

```
### Unverified Capabilities (excluded from ranking)

These were found in documentation or comments but could not be confirmed in code:

| Capability | Where mentioned | Why unverified |
|---|---|---|
| Real-time streaming | README.md:12 | No WebSocket code found in source |
| ML prediction | comments in pipeline.py:88 | scikit-learn imported but no model code |
```

#### G1.4 — Prerequisite Chain Validation
For each method, the agent must trace the full prerequisite chain — not just "data exists" but "data exists in the format this method needs." Example:

```
Method: GARCH Volatility
Prerequisite: daily returns timeseries, >250 data points
Chain check:
  ✓ PriceTimeSeries has daily OHLCV (models.py:15)
  ✓ calculate_returns() converts prices to returns (analytics.py:42)
  ✗ No check for minimum data length — need to verify >250 days available
  → Classification: LOW_EFFORT (not READY — needs length validation)
```

#### G1.5 — Knowledge Source Fidelity
When extracting methods from course material, the agent must distinguish between:
- **Methods the course teaches how to implement** (with formulas, pseudocode, examples) → HIGH confidence
- **Methods the course only mentions** (referenced but not explained) → LOW confidence
- **Methods the agent infers** (not in the course but related) → NOT ALLOWED in the catalog

Low-confidence methods are flagged in the knowledge catalog. Methods the agent infers (not explicitly in the source) are excluded entirely — the agent must not add analytics that aren't in the knowledge source.

### Layer 2: Specification-Time (prevent infeasible requirements)

These guardrails ensure the spec doesn't promise what can't be delivered.

#### G2.1 — Traceability Matrix
Every requirement in the spec must trace back to:
- A selected analytic from the discovery report, AND
- A specific method in the knowledge catalog, AND
- Specific capabilities in the inventory that support it

If a requirement can't complete this chain, it must be flagged for review.

Format in `.clarity/spec.md`:
```markdown
FR-007: The skill shall calculate Value at Risk (VaR) at 95% and 99% confidence levels.
  - **Discovery:** Analytic #7 (Tier 2, MODERATE effort)
  - **Method:** Value at Risk, knowledge.md (Chapter 5, p.88)
  - **Capabilities:** PriceTimeSeries (models.py:15), calculate_returns() (analytics.py:42), scipy.stats.norm (requirements.txt:3)
```

#### G2.2 — No Phantom Requirements
Clarity must NOT add requirements for analytics that weren't in the user's selection. If clarity identifies additional analytics that would be useful, it lists them as suggestions at the end of the spec — not as requirements. Only the user can expand the scope.

#### G2.3 — Feasibility-Aware Scenarios
Holdout scenarios must include **feasibility boundary tests** — scenarios that specifically test what happens at the edge of feasibility:

| Scenario type | What it tests | Example |
|---|---|---|
| **Insufficient data** | Analytics gracefully handles too little data | "GARCH with 30 days of data → clear error, not garbage output" |
| **Missing input** | Analytics handles absent optional data | "Sharpe ratio without risk-free rate → uses 0% default or clear error" |
| **Degenerate case** | Single asset, empty portfolio, zero variance | "Efficient frontier with 1 asset → meaningful error, not crash" |
| **Format mismatch** | Data exists but in wrong format | "Returns as percentages vs decimals → correct handling or clear error" |

These scenarios are specifically designed to catch the case where the agent built something that works on the happy path but breaks on real-world edge cases.

### Layer 3: Build-Time (prevent garbage implementations)

These guardrails ensure the built skill actually computes correct results.

#### G3.1 — Discovery Context in Skill Brief
The skill brief passed to agent-skill-creator must include the `## Discovery Context` section (defined in "From Discovery to SPECIFY" above). This ensures the builder knows:
- What repo code already exists (build on it, don't reimplement)
- What the method definition is (from the knowledge source, not from the agent's training data)
- What the prerequisites are (verified by probes)

#### G3.2 — Method Definition Fidelity
When the knowledge source provides a formula or algorithm, the skill brief must include it verbatim. The builder implements the formula from the course — not a different version from its training data. This prevents subtle correctness errors where the agent implements a "standard" formula that differs from what the course teaches.

Example in skill brief:
```markdown
### Sharpe Ratio (from quantitative-finance.pdf, Chapter 3, p.42)

Formula: SR = (Rp - Rf) / σp

Where:
- Rp = annualized portfolio return
- Rf = annualized risk-free rate
- σp = annualized standard deviation of portfolio returns

Annualization: multiply daily return by 252, multiply daily std by √252

NOTE: Use this exact formula. Do not substitute alternative definitions
(e.g., do not use semi-deviation, do not use geometric mean).
```

### Layer 4: Verification-Time (catch what slipped through)

These guardrails ensure holdout scenarios actually validate feasibility, not just happy-path correctness.

#### G4.1 — Feasibility Boundary Scenarios (defined in G2.3)
At least 20% of holdout scenarios must be feasibility boundary tests. If clarity generates 15 scenarios, at least 3 must test insufficient data, missing inputs, or degenerate cases.

#### G4.2 — Numerical Validation Scenarios
For analytics that produce numerical outputs, at least one scenario must include a **known-answer test** — a hand-calculable example from the course material where the expected output is computed independently:

```markdown
SC-007: VaR at 99% confidence — known answer

Input: 10 daily returns: [-0.02, 0.01, -0.03, 0.02, -0.01, 0.015, -0.025, 0.005, -0.01, 0.02]
Expected: Parametric VaR at 99% = mean - 2.326 × std = {computed value}
Source: Course example, Chapter 5, p.92

This scenario validates that the implementation matches the course formula,
not just that it produces a number.
```

#### G4.3 — Regression Guard for Discovery-Originated Skills
When a discovery-originated skill is later updated via `/cliskill update`, all original feasibility boundary scenarios must be preserved and re-run. A regression in a feasibility boundary test is classified as HIGH PRIORITY in the repair loop.

---

## Summary: Guardrail Checkpoint Map

```
DISCOVER
  ├── D1: Evidence-based inventory (G1.1) — cite file:line for every claim
  ├── D1: Unverified category (G1.3) — exclude what can't be confirmed
  ├── D2: Knowledge source fidelity (G1.5) — only methods the source teaches
  ├── D3: Feasibility probes (G1.2) — test before classifying
  ├── D3: Prerequisite chain validation (G1.4) — trace the full chain
  └── Report: unverified section visible, blocked section with reasons

SPECIFY
  ├── Traceability matrix (G2.1) — every requirement → discovery + knowledge + capability
  ├── No phantom requirements (G2.2) — only user-selected analytics
  └── Feasibility boundary scenarios (G2.3) — ≥20% of scenarios test edges

BUILD
  ├── Discovery context in brief (G3.1) — builder knows what exists
  └── Method definition fidelity (G3.2) — formula from source, not training data

VERIFY
  ├── Feasibility boundary scenarios (G4.1) — edge cases tested
  ├── Numerical validation (G4.2) — known-answer tests from course
  └── Regression guard (G4.3) — boundary tests preserved on update
```

The guardrails form a **layered defense**: each layer catches failure modes the previous layer might miss. An agent that hallucinated a capability in D1 gets caught by the probe in D3. A probe that passed but the implementation is wrong gets caught by the known-answer test in VERIFY. A spec that's correct but edge cases weren't considered gets caught by feasibility boundary scenarios.
