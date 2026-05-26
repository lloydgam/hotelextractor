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

## Orchestrator Protocol (Agent Teams)

When the user asks to run the hotel pipeline, **act as Orchestrator using the Agent tool**. Do not call `pipeline.py` directly — spawn real Claude subagents instead.

`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` is set in `.claude/settings.json`, enabling the Agent tool.

---

### Step 1 — Parallel: Setup Agent + Searcher Agent

Spawn both agents simultaneously (two Agent tool calls in one message):

**Setup Agent prompt:**
> Set up the HotelAIExtractor environment. Run:
> ```bash
> mkdir -p output data data/logs && pip3 install -q openpyxl
> echo "Setup complete"
> ```
> Report done when finished.

**Searcher Agent prompt:**
> You are the Searcher agent for HotelAIExtractor. Run the hotel search and return results as JSON.
> ```bash
> python3 scripts/search.py --agent --destination {destination} --checkin {checkin} --checkout {checkout} --max-price {max_price} --min-rating {min_rating} --max-results 20
> ```
> Capture the JSON array printed to stdout and return it verbatim.

Wait for the Searcher to return the JSON hotel list before proceeding.

---

### Step 2 — Extractor Agent

Spawn one Extractor agent with the raw hotel JSON from Step 1:

**Extractor Agent prompt:**
> You are the Extractor agent for HotelAIExtractor. Normalize this raw hotel list.
> ```bash
> python3 scripts/extract.py --nights {nights} --hotels '{raw_hotels_json}'
> ```
> Return the JSON array printed to stdout verbatim.

---

### Step 3 — Parallel: Processor Agent + Exporter Agent

Spawn both agents simultaneously with the extracted hotel JSON from Step 2:

**Processor Agent prompt:**
> You are the Processor agent for HotelAIExtractor. Filter this hotel list by budget and rating.
> ```bash
> python3 scripts/process.py --max-price {max_price} --min-rating {min_rating} --hotels '{extracted_json}'
> ```
> Return the JSON array of hotels that passed filters verbatim.

**Exporter Agent prompt:**
> You are the Exporter agent for HotelAIExtractor. Write this hotel list to Excel.
> ```bash
> python3 scripts/export.py --path output/hotels_{destination}_{checkin}.xlsx --hotels '{extracted_json}'
> ```
> Return the JSON result verbatim.

---

### Step 4 — Sort and display

Take the Processor output (passed hotels). Sort by `{sort_by}` (rating desc, or price asc). Print the final results table and confirm the Excel path.

---

## Guidelines

- When asked to run the pipeline: use the **Agent tool** to spawn subagents — this is what makes it Agent Teams
- `scripts/pipeline.py` remains as a standalone Python fallback (e.g. for the tmux demo)
- Each agent script exports one importable function AND a `__main__` CLI for agent use
- Never over-engineer — each agent does one thing and exits
- Keep `data/` for intermediate files, `output/` for final deliverables
- `dangerouslyAllowAll: true` is set in `.claude/settings.json` — no permission prompts
