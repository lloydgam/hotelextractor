# HotelAIExtractor

**A hotel price intelligence system powered by Claude Code Agent Teams.**

One sentence triggers a coordinated team of real Claude agents — each with one role — that search, extract, filter, and export hotel data through a pipeline of typed JSON handoffs.

---

## Purpose

HotelAIExtractor demonstrates **Claude Code Agent Teams**: an Orchestrator spawning specialized Claude subagents via the `Agent` tool, coordinating parallel execution, and assembling a final result — all from a single natural-language request.

The hotel search is the use case. The pattern — Orchestrator + specialized agents + parallel stages + typed handoffs — applies to any multi-step workflow.

---

## How It Works

```
User types one sentence
        │
        ▼
   Orchestrator (Claude Code session)
        │   CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
        │
        │   Agent tool ×2 — parallel
        ├── Setup Agent        → installs deps, creates folders
        └── Searcher Agent     → discovers hotels, returns raw JSON
                │
                ▼
           Extractor Agent     → normalizes: name, price, rating, location
                │
                │   Agent tool ×2 — parallel
                ├── Processor Agent  → applies filters, returns passed hotels
                └── Exporter Agent   → writes Excel, returns confirmation
                        │
                        ▼
                 Orchestrator sorts → prints results table
```

- **Real subagents:** each stage is a genuine Claude instance with its own context and tools
- **Parallel spawning:** Setup + Searcher launch simultaneously; Processor + Exporter launch simultaneously
- **Typed handoffs:** agents communicate via JSON passed in prompts — no shared state
- **Self-directing:** `CLAUDE.md` Orchestrator Protocol drives all behavior; nothing is configured manually

---

## How to Run

Open this project in Claude Code and type a search request:

```bash
cd HotelAIExtractor
claude
```

Then in chat:
```
Search Bangkok hotels, check-in 2026-06-01, check-out 2026-06-04,
max price $150, min rating 7.5, sort by rating
```

Claude reads the Orchestrator Protocol from `CLAUDE.md` and coordinates the full agent team. No scripts to run, no configuration needed.

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

| Agent | Role |
|---|---|
| **Orchestrator** | Main Claude session — spawns subagents via `Agent` tool, assembles final table |
| **Setup** | Installs deps, creates `output/`, `data/` directories |
| **Searcher** | Discovers hotels, returns raw JSON array |
| **Extractor** | Normalizes raw records — price, rating, location, totals |
| **Processor** | Filters by max price and min rating |
| **Exporter** | Writes sorted hotels to Excel |

Each agent calls a dedicated script via Bash and returns JSON to the Orchestrator.

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

Claude extracts all of these from your natural-language request.

---

## Project Structure

```
HotelAIExtractor/
├── README.md                  ← You are here
├── CLAUDE.md                  ← Agent roles + Orchestrator Protocol
├── WORKSHOP_GUIDE.md          ← Step-by-step presenter guide
├── .claude/
│   └── settings.json          ← CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
├── scripts/
│   ├── search.py              ← Searcher agent tool
│   ├── extract.py             ← Extractor agent tool
│   ├── process.py             ← Processor agent tool
│   ├── export.py              ← Exporter agent tool
│   ├── run_demo.sh            ← tmux architecture visualization
│   └── start_agent_pane.sh    ← Per-agent pane styling
├── data/
│   └── processed_*.json       ← Sorted JSON output
└── output/
    └── hotels_*.xlsx          ← Final Excel reports
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| AI orchestration | Claude Code + Claude Sonnet |
| Agent spawning | `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` + `Agent` tool |
| Agent instructions | `CLAUDE.md` Orchestrator Protocol |
| Agent I/O | JSON over stdout — each script has `--agent` mode |
| Architecture visualization | tmux 5-pane layout with per-agent color coding |
| Data | Realistic mock hotel data (Bangkok, Singapore) |
| Export | `openpyxl` (Excel), JSON |

---

## Extending the Project

| Goal | What to change |
|---|---|
| Real hotel data | Replace `search.py` with a hotel API call |
| Different destination | Pass it in your chat message — no reconfiguration |
| Email the report | Add a Notifier agent to the Orchestrator Protocol |
| Google Sheets output | Replace `export.py` |
| Multi-city search | Spawn one Searcher Agent per city simultaneously |
| Add review sentiment | Add Analyst agent between Extractor and Processor |
| Schedule daily runs | Claude Code `/schedule` |

---

## Demo

See `WORKSHOP_GUIDE.md` for the full presenter guide — step-by-step walkthrough, talking points for each Agent tool call, and Q&A.

---

## Note on Data Source

The Searcher uses realistic mock data modeled on real Bangkok and Singapore hotels. To use live data, replace `scripts/search.py` with calls to a hotel data API (e.g. RapidAPI Hotels, Expedia Affiliate Network). All other agents are unchanged.
