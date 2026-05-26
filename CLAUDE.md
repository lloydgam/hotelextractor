# HotelAIExtractor

## Project Overview
A **Hotel Price Intelligence System** powered by a streaming multi-agent pipeline. Each hotel flows through a chain of specialized agents the moment it is discovered — no waiting for the full batch. The Orchestrator coordinates the team; each agent has one job and hands off immediately.

---

## Agent Team

### Orchestrator (Claude — main session)
- Receives user filters, asks nothing, runs immediately
- Spawns Setup Agent and pipeline in parallel
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

## Guidelines

- `scripts/pipeline.py` is the single entry point — it orchestrates all agents internally
- Each agent script exports one function: `search_hotels()`, `extract_one()`, `process_one()`, `append_hotel()`
- Never over-engineer — each agent does one thing and exits
- Keep `data/` for intermediate files, `output/` for final deliverables
- `dangerouslyAllowAll: true` is set in `.claude/settings.json` — no permission prompts
