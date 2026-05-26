# HotelAIExtractor

**A hotel price intelligence system built as a streaming multi-agent pipeline.**

One sentence triggers a coordinated team of AI agents that search, extract, process, and export hotel data — with each item flowing through the pipeline the moment it is found, not after the full batch is collected.

---

## Purpose

HotelAIExtractor is a **demonstration project** for the streaming multi-agent pipeline pattern. It uses hotel price search as a real-world use case to show how:

- A team of specialized agents can replace a single monolithic script
- Streaming (per-item) processing eliminates batch wait time
- Parallel execution at the right stages cuts end-to-end latency
- Claude Code + `CLAUDE.md` creates a self-directing AI workflow

The pattern demonstrated here applies to any domain where data arrives as a stream and each item needs to be processed, filtered, and exported independently.

---

## How It Works

```
User types one sentence
        │
        ▼
   Orchestrator (Claude)
        │
        ├── Setup Agent         → installs deps, creates folders
        │
        └── Streaming Pipeline  → for each hotel found:
                │
                ▼
           [Searcher]           yields one hotel at a time
                │
                ▼
           [Extractor]          normalizes: name, price, rating, location
                │
                ▼
        [Processor ∥ Exporter]  filter + write Excel  ← run in parallel
                │
                ▼
             ✓ done             result visible immediately

   After all 20:  sort → rewrite Excel → print table
```

Key behaviors:
- **Streaming:** hotels enter the pipeline one at a time, not as a batch
- **Concurrent:** multiple hotels move through the pipeline simultaneously (up to 8 threads)
- **Parallel stages:** Processor and Exporter run at the same time on each hotel
- **Self-stopping:** pipeline halts as soon as 20 hotels are collected

---

## Quick Start

**Prerequisites:** Python 3.8+, Claude Code

```bash
# 1. Open the project
cd HotelAIExtractor
claude

# 2. Paste a search request into Claude Code chat
Search Bangkok hotels, check-in 2026-06-01, check-out 2026-06-04,
max price $150, min rating 7.5, sort by rating

# 3. Claude runs the full pipeline automatically
#    Results are printed in chat and saved to output/
```

**Or run directly:**

```bash
python3 scripts/pipeline.py
```

---

## Output

| File | Description |
|---|---|
| `output/hotels_{destination}_{date}.xlsx` | Formatted Excel report |
| `data/processed_{destination}_{date}.json` | Sorted JSON dataset |

**Excel columns:** `#`, Hotel Name, Price/Night (USD), Total Price (3n), Rating, Location  
Styled with dark blue header, alternating row shading, frozen top row.

---

## Agent Team

| Agent | File | Role |
|---|---|---|
| **Orchestrator** | Claude (main session) | Coordinates the team, prints results |
| **Setup** | — | Installs deps, creates folders |
| **Searcher** | `scripts/search.py` | Streaming generator — yields hotels one at a time |
| **Extractor** | `scripts/extract.py` | Normalizes one raw hotel record |
| **Processor** | `scripts/process.py` | Applies filters to one hotel |
| **Exporter** | `scripts/export.py` | Thread-safe Excel append per hotel |
| **Pipeline** | `scripts/pipeline.py` | Wires agents together, manages concurrency |

---

## Search Parameters

```python
run_pipeline(
    destination = "Bangkok",      # city or region
    checkin     = "2026-06-01",   # ISO date
    checkout    = "2026-06-04",   # ISO date
    max_price   = 150.0,          # USD per night
    min_rating  = 7.5,            # guest review score
    sort_by     = "rating",       # "rating" or "price"
    max_results = 20,             # stop after N hotels
)
```

---

## Project Structure

```
HotelAIExtractor/
├── README.md              ← You are here
├── CLAUDE.md              ← Agent team operating manual (read by Claude automatically)
├── WORKSHOP_GUIDE.md      ← Step-by-step presenter guide for live demos
├── .claude/
│   └── settings.json      ← Project permissions (dangerouslyAllowAll: true)
├── scripts/
│   ├── pipeline.py        ← Entry point — orchestrates the full streaming pipeline
│   ├── search.py          ← Searcher: streaming hotel generator
│   ├── extract.py         ← Extractor: normalize one hotel
│   ├── process.py         ← Processor: filter one hotel
│   └── export.py          ← Exporter: thread-safe Excel writer
├── data/                  ← Intermediate and processed JSON files
└── output/                ← Final Excel reports
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| AI orchestration | Claude Code + Claude Sonnet |
| Agent instructions | `CLAUDE.md` |
| Pipeline concurrency | Python `threading` + `concurrent.futures` |
| Data | Mock hotel data (Agoda-compatible fallback) |
| Export | `openpyxl` (Excel), JSON |
| HTTP (for live data) | `requests` + `beautifulsoup4` |

---

## Extending the Project

| Goal | What to change |
|---|---|
| Real hotel data | Replace `search.py` with a hotel API call |
| Different destination | Change `destination` param in `pipeline.py` |
| Email the report | Add a Notifier agent after `export.py` |
| Google Sheets output | Replace `export.py` with Sheets API calls |
| Multi-city search | Spawn one `run_pipeline()` per city in parallel |
| Morning automation | Add a cron job calling `python3 scripts/pipeline.py` |
| Review sentiment | Add an Analyst agent between Extractor and Processor |

---

## Demo

See `WORKSHOP_GUIDE.md` for a complete step-by-step presenter guide including talking points, live narration cues, and common Q&A.

---

## Note on Data Source

Agoda's website uses JavaScript rendering and bot protection that blocks server-side HTTP requests. The Searcher currently uses realistic mock data modeled on real Bangkok hotels and districts. To use live data, replace `scripts/search.py` with calls to a hotel data API (e.g. RapidAPI Hotels, Expedia Affiliate Network). All other agents remain unchanged.
