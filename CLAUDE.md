# HotelAIExtractor

## Project Overview
A **Hotel Price Intelligence System** powered by a coordinated agent team. The orchestrator receives user search filters and delegates to specialized agents that search, extract, process, and export hotel data — producing a sorted Excel report automatically.

---

## Agent Team

### Orchestrator (Claude — main session)
- Receives user filters, validates nothing, asks nothing
- Spawns and coordinates the agent team
- Collects results, prints the final table, confirms output file

### Agent: Setup
- **Role:** Environment preparation
- **Tasks:** Create folder structure (`output/`, `data/`, `scripts/`), install Python dependencies
- **Runs:** Once at project start or on first run

### Agent: Searcher
- **Role:** Query Agoda with user filters, collect raw hotel listings
- **Tasks:** Build search URL, fetch pages, stop once 20+ results are in hand
- **Output:** Raw data saved to `data/raw_{destination}_{YYYY-MM-DD}.json`

### Agent: Extractor
- **Role:** Parse raw HTML/JSON, pull structured fields
- **Tasks:** Extract hotel name, price, rating, location from raw data
- **Output:** Structured records saved to `data/extracted_{destination}_{YYYY-MM-DD}.json`

### Agent: Processor
- **Role:** Filter, deduplicate, sort, and trim results
- **Tasks:** Apply user filters (max price, min rating, property type, star rating), sort by requested field, keep top 20
- **Output:** Clean dataset ready for export

### Agent: Exporter
- **Role:** Generate deliverables
- **Tasks:** Write Excel file to `output/hotels_{destination}_{YYYY-MM-DD}.xlsx`, return table for inline display

---

## Execution Flow

```
User Input
    │
    ▼
Orchestrator
    ├── [parallel] Setup Agent
    └── [parallel] Searcher Agent
            │
            ▼
        Extractor Agent
            │
            ▼
        Processor Agent
            │
            ▼
        Exporter Agent
            │
            ▼
    Print table in chat + confirm Excel path
```

**Rules:**
- Setup and Searcher run in parallel on first launch
- Extractor, Processor, Exporter run sequentially (each depends on prior output)
- Stop fetching at 20+ results — no over-pagination
- Never ask the user to confirm or clarify — run immediately with what was given

---

## Data Fields

| Field | Description |
|---|---|
| **Hotel Name** | Full property name |
| **Price** | Nightly rate (note currency) |
| **Rating** | Guest review score |
| **Location** | District or area |

---

## Search Filters

| Filter | Notes |
|---|---|
| **Destination** | City or region — required |
| **Check-in / Check-out** | Date range — required |
| **Max Price** | Upper budget limit |
| **Min Rating** | e.g. 7.0+ |
| **Sort By** | `price` (default), `rating`, `distance` |
| **Star Rating** | 1–5 stars |
| **Property Type** | hotel, hostel, resort, apartment |

---

## Output

- Excel report: `output/hotels_{destination}_{YYYY-MM-DD}.xlsx`
- Raw data: `data/raw_{destination}_{YYYY-MM-DD}.json`
- Extracted data: `data/extracted_{destination}_{YYYY-MM-DD}.json`

---

## Guidelines

- Use the `Agent` tool to spawn each named agent above
- Run independent agents in a single message (parallel spawning)
- Run dependent agents sequentially, only after prior output is ready
- Use Python: `requests`, `beautifulsoup4`, `openpyxl`, `pandas`, `lxml`
- Keep scripts in `scripts/` and make them reusable for future runs
- Never over-engineer — each agent does one thing and exits
