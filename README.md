# HotelAIExtractor

**A hotel price intelligence system built on Claude Code Agent Teams.**

One sentence triggers a lead Claude session that creates a 4-teammate agent team. Each teammate owns one stage, claims its task from a shared task list, communicates through files, and reports back — with Processor and Exporter running simultaneously the moment Extractor finishes.

---

## Purpose

HotelAIExtractor demonstrates **Claude Code Agent Teams**: a lead session creating full Claude Code teammates that coordinate through a shared task list, claim work independently, and communicate directly — not through the lead's context.

The hotel search is the use case. The pattern — lead + named teammates + shared task list + file-based handoffs — applies to any multi-step workflow with parallel stages.

---

## How It Works

```
User types one sentence
        │
        ▼
   Lead (Orchestrator Claude Code session)
        │   CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
        │   teammateMode: tmux
        │
        │   Creates team + task list
        ▼
   ┌─────────────┬──────────────┬──────────────┬─────────────┐
   │  SEARCHER   │  EXTRACTOR   │  PROCESSOR   │  EXPORTER   │
   │  teammate   │  teammate    │  teammate    │  teammate   │
   └──────┬──────┴──────┬───────┴──────┬───────┴──────┬──────┘
          │             │              │              │
   claims [search]      │              │              │
   writes raw JSON      │              │              │
          │             │              │              │
          └──► unblocks [extract]      │              │
                        │              │              │
               claims [extract]        │              │
               writes extracted JSON   │              │
                        │              │              │
                        └──► unblocks [process] and [export] simultaneously
                                       │              │
                              claims [process] claims [export]
                              filters hotels   writes Excel
                              writes processed │
                                       │        │
                                       └────────┘
                                            │
                                        Lead sorts → prints table
```

Key behaviors:
- **Full teammate sessions:** each role is a separate Claude Code instance with its own context window and tmux pane
- **Shared task list:** dependencies are enforced automatically — `process` and `export` stay blocked until `extract` completes, then both unblock simultaneously
- **File-based handoffs:** teammates communicate through `data/` files, not through the lead's context
- **Self-directing:** `CLAUDE.md` defines the Orchestrator Protocol; the lead reads it and runs

---

## How to Run

Open the project in Claude Code and type a search request:

```bash
cd HotelAIExtractor
claude
```

Then in chat:
```
Search Bangkok hotels, check-in 2026-06-01, check-out 2026-06-04,
max price $150, min rating 7.5, sort by rating
```

The lead reads the Orchestrator Protocol from `CLAUDE.md`, creates the agent team, sets up the task list, and each teammate claims its task when dependencies clear. In tmux, each teammate appears in its own pane.

---

## Output

| File | Description |
|---|---|
| `output/hotels_{destination}_{date}.xlsx` | Formatted Excel report |
| `data/processed_{destination}_{date}.json` | Filtered sorted JSON |
| `data/extracted_{destination}_{date}.json` | Normalized (pre-filter) JSON |
| `data/raw_{destination}_{date}.json` | Raw search output |

**Excel columns:** `#`, Hotel Name, Price/Night (USD), Total Price (3n), Rating, Location  
Styled with dark blue header, alternating row shading, frozen top row.

---

## Agent Team

| Role | Type | Task | Reads | Writes |
|------|------|------|-------|--------|
| **Lead** | Claude Code session | Coordinates team, prints final table | — | — |
| **Searcher** | Teammate | `search` | — | `data/raw_*.json` |
| **Extractor** | Teammate | `extract` (depends: search) | `data/raw_*.json` | `data/extracted_*.json` |
| **Processor** | Teammate | `process` (depends: extract) | `data/extracted_*.json` | `data/processed_*.json` |
| **Exporter** | Teammate | `export` (depends: extract) | `data/extracted_*.json` | `output/hotels_*.xlsx` |

`process` and `export` depend on `extract` but not each other — they run in parallel.

---

## Search Parameters

```
destination   City or region (e.g. "Bangkok", "Singapore")
checkin       ISO date — e.g. "2026-06-01"
checkout      ISO date — e.g. "2026-06-04"
max_price     USD per night ceiling
min_rating    Guest review score floor (0–10)
sort_by       "rating" (default) or "price"
max_results   Cap on results — default 20
```

The lead extracts all of these from your natural-language request.

---

## Project Structure

```
HotelAIExtractor/
├── README.md                  ← You are here
├── CLAUDE.md                  ← Agent team roles + Orchestrator Protocol
├── WORKSHOP_GUIDE.md          ← Step-by-step presenter guide
├── .claude/
│   └── settings.json          ← CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1, teammateMode: tmux
├── scripts/
│   ├── search.py              ← Searcher teammate tool  (--output for file handoff)
│   ├── extract.py             ← Extractor teammate tool (--input / --output)
│   ├── process.py             ← Processor teammate tool (--input / --output)
│   └── export.py              ← Exporter teammate tool  (--input)
├── data/
│   ├── raw_*.json             ← Searcher output
│   ├── extracted_*.json       ← Extractor output
│   └── processed_*.json       ← Processor output
└── output/
    └── hotels_*.xlsx          ← Final Excel report
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| AI coordination | Claude Code Agent Teams |
| Team feature flag | `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` |
| Display mode | `"teammateMode": "tmux"` — one pane per teammate |
| Team instructions | `CLAUDE.md` Orchestrator Protocol |
| Inter-teammate I/O | File-based JSON handoffs via `data/` |
| Export | `openpyxl` (Excel) |
| Data | Realistic mock hotel data (Bangkok, Singapore) |

---

## Extending the Project

| Goal | What to change |
|------|----------------|
| Real hotel data | Replace `search.py` with a hotel API call |
| Different destination | Pass it in your chat message |
| Email the report | Add a Notifier teammate to the Orchestrator Protocol |
| Google Sheets output | Replace `export.py` |
| Multi-city search | Spawn one Searcher teammate per city — parallel `search` tasks |
| Add review sentiment | Add Analyst teammate between Extractor and Processor |
| Schedule daily runs | Claude Code `/schedule` |

---

## Note on Data Source

The Searcher uses realistic mock data modeled on real Bangkok and Singapore hotels. To use live data, replace `scripts/search.py` with calls to a hotel data API (e.g. RapidAPI Hotels, Expedia Affiliate Network). The output file schema is the contract — all other teammates are unchanged.
