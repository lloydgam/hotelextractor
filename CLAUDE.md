# HotelAIExtractor

## Project Overview
A **Hotel Price Intelligence System** powered by a streaming multi-agent pipeline. Each hotel flows through a chain of specialized agents the moment it is discovered — no waiting for the full batch. The Orchestrator coordinates the team; each agent has one job and hands off immediately.

---

## Agent Team

### Orchestrator (Claude — lead session)
- Receives user filters, asks nothing, runs immediately
- Creates the agent team, sets up the task list, monitors progress
- Prints the final results table and confirms the Excel path

### Agent: Setup
- **Role:** Environment preparation
- **Runs:** Once on first run (or when deps are missing)
- **Tasks:** Create `output/`, `data/`, `scripts/`; install Python dependencies

### Agent: Searcher  `scripts/search.py`
- **Role:** Discover hotels one at a time (streaming generator)
- **Behavior:** Yields each hotel the moment it is found — does not wait to collect all results before passing them on
- **Stops:** As soon as 20 hotels have been yielded

### Agent: Extractor  `scripts/extract.py`
- **Role:** Normalize one raw hotel record
- **Triggered:** Immediately when Searcher yields a hotel
- **Output:** `{hotel_name, price_usd, total_price_usd, rating, location, nights}`

### Agent: Processor  `scripts/process.py`
- **Role:** Apply filters to one extracted hotel
- **Runs in parallel with:** Exporter (same hotel, same moment)
- **Returns:** Hotel if it passes all filters, else `None`

### Agent: Exporter  `scripts/export.py`
- **Role:** Append one hotel row to the Excel file (thread-safe)
- **Runs in parallel with:** Processor (same hotel, same moment)
- **Output:** Appends to `output/hotels_{destination}_{YYYY-MM-DD}.xlsx`

---

## Streaming Pipeline Flow

Every hotel travels the same path independently and concurrently:

```
[Searcher] yields hotel_1 ─────────────────────────────────────────────────┐
[Searcher] yields hotel_2 ─────────────────────────────────┐               │
[Searcher] yields hotel_3 ─────────────────┐               │               │
                                           ▼               ▼               ▼
                                      [Extractor]     [Extractor]     [Extractor]
                                           │               │               │
                                    [Proc ∥ Exp]    [Proc ∥ Exp]    [Proc ∥ Exp]
                                           │               │               │
                                        ✓ done          ✓ done          ✓ done
                                                              │
                                                    Final sort + Excel rewrite
                                                    Print results table
```

**Rules:**
- Setup and first pipeline run launch in parallel
- Within each hotel: Extractor runs first (sequential), then Processor + Exporter fire simultaneously (parallel)
- All hotels flow through the pipeline concurrently (up to 8 threads)
- Stop at 20 results — no over-fetching
- Never ask the user to confirm — run immediately with given filters

---

## Entry Point

```bash
python3 scripts/pipeline.py
```

Or call from Orchestrator:

```python
from scripts.pipeline import run_pipeline

run_pipeline(
    destination = "Bangkok",
    checkin     = "2026-06-01",
    checkout    = "2026-06-04",
    max_price   = 150.0,
    min_rating  = 7.5,
    sort_by     = "rating",   # or "price"
    max_results = 20,
)
```

---

## Data Fields

| Field | Description |
|---|---|
| **hotel_name** | Full property name |
| **price_usd** | Nightly rate in USD |
| **total_price_usd** | price × nights |
| **rating** | Guest review score (0–10) |
| **location** | District or area |
| **nights** | Length of stay |

---

## Search Filters

| Filter | Notes |
|---|---|
| **destination** | City or region — required |
| **checkin / checkout** | ISO date strings — required |
| **max_price** | Upper budget limit per night |
| **min_rating** | e.g. `7.5` |
| **sort_by** | `rating` (default) or `price` |
| **max_results** | Cap on results, default `20` |

---

## File Outputs

| File | Description |
|---|---|
| `output/hotels_{destination}_{checkin}.xlsx` | Final sorted Excel report |
| `data/processed_{destination}_{checkin}.json` | Final sorted JSON |

---

## Orchestrator Protocol (Agent Teams)

When the user asks to run the hotel pipeline, use the **Agent Teams** feature — not the `Agent` tool. Agent Teams creates separate full Claude Code sessions as teammates that share a task list and coordinate independently.

`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` and `"teammateMode": "tmux"` are set in `.claude/settings.json`.

---

### Step 1 — Create the team

Tell Claude Code to create the agent team:

> "Create an agent team for the hotel pipeline with 4 teammates: **searcher**, **extractor**, **processor**, and **exporter**."

---

### Step 2 — Set up the task list

Create these 4 tasks with their dependencies:

| Task | Teammate | Depends on | Parallel with |
|------|----------|-----------|---------------|
| `search` | searcher | — | — |
| `extract` | extractor | `search` | — |
| `process` | processor | `extract` | `export` |
| `export` | exporter | `extract` | `process` |

`process` and `export` both depend on `extract` but not each other — they unblock and run **simultaneously** when `extract` completes.

---

### Task definitions

**`search` — searcher teammate**
```bash
mkdir -p data output && pip3 install -q openpyxl
python3 scripts/search.py --agent \
  --destination {destination} --checkin {checkin} --checkout {checkout} \
  --max-price {max_price} --min-rating {min_rating} --max-results 20 \
  --output data/raw_{destination}_{checkin}.json
```

**`extract` — extractor teammate**
```bash
python3 scripts/extract.py \
  --input  data/raw_{destination}_{checkin}.json \
  --nights {nights} \
  --output data/extracted_{destination}_{checkin}.json
```

**`process` — processor teammate** *(runs in parallel with export)*
```bash
python3 scripts/process.py \
  --input     data/extracted_{destination}_{checkin}.json \
  --max-price {max_price} --min-rating {min_rating} \
  --output    data/processed_{destination}_{checkin}.json
```

**`export` — exporter teammate** *(runs in parallel with process)*
```bash
python3 scripts/export.py \
  --input data/extracted_{destination}_{checkin}.json \
  --path  output/hotels_{destination}_{checkin}.xlsx
```

---

### Step 3 — Monitor

Watch the task list. When `search` completes, `extract` unblocks automatically. When `extract` completes, both `process` and `export` unblock simultaneously. Use `Shift+Down` to visit individual teammate sessions.

---

### Step 4 — Finalize

After all 4 tasks complete:
1. Read `data/processed_{destination}_{checkin}.json` — the filtered hotel list
2. Sort by `{sort_by}` (rating descending, or price ascending)
3. Ask the **exporter** teammate to rewrite the Excel with the sorted filtered list:
   > "Run: `python3 scripts/export.py --input data/processed_{destination}_{checkin}.json --path output/hotels_{destination}_{checkin}.xlsx`"
4. Print the final results table

---

### How data flows between teammates

Teammates never pass data through the Lead's context — they communicate through files:

```
data/raw_{destination}_{checkin}.json        ← searcher writes
data/extracted_{destination}_{checkin}.json  ← extractor writes, processor + exporter read
data/processed_{destination}_{checkin}.json  ← processor writes
output/hotels_{destination}_{checkin}.xlsx   ← exporter writes
```

---

## Guidelines

- When asked to run the pipeline: **create an agent team** with teammates — not the `Agent` tool (that is subagents)
- Each agent script has a `--input` / `--output` CLI for file-based teammate handoffs
- Never over-engineer — each teammate does one task and exits
- Keep `data/` for intermediate files, `output/` for final deliverables
- `dangerouslyAllowAll: true` is set in `.claude/settings.json` — no permission prompts
