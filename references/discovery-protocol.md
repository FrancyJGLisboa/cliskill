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

Write the inventory to `.cliskill/discovery/capabilities.md`:

```markdown
# Capability Inventory

## Data Structures
- {name}: {description, fields, relationships}

## Functions
- {name}({params}): {what it does, return type}

## Data Sources
- {name}: {what data, format, freshness}

## Existing Pipelines
- {name}: {steps, input → output}

## Library Capabilities
- {library}: {what it enables that isn't directly in the code yet}
```

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

Write the matrix to `.cliskill/discovery/cross-reference.md`:

```markdown
# Cross-Reference Matrix

| Method | Data | Functions | Feasibility | Effort | Notes |
|--------|------|-----------|-------------|--------|-------|
| Sharpe Ratio | data_ready | already_implemented | READY | Wire up | `calculate_returns()` exists |
| Monte Carlo | data_ready | buildable | MODERATE | numpy/scipy available | Need to implement simulation loop |
| GARCH Volatility | data_ready | buildable | MODERATE | statsmodels available | `arch` library needed |
| Sentiment Analysis | data_blocked | complex_build | BLOCKED | No text data source | Would need news API |
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
├── capabilities.md        # Phase D1 output
├── knowledge.md           # Phase D2 output
├── cross-reference.md     # Phase D3 output
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
