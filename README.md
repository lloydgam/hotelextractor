# HotelAIExtractor

**A hotel price intelligence system built as a streaming multi-agent pipeline.**

One sentence triggers a coordinated team of real Claude AI agents that search, extract, process, and export hotel data — with each item flowing through the pipeline the moment it is found, not after the full batch is collected.

---

## Purpose

HotelAIExtractor is a **demonstration project** for two patterns at once:

1. **Claude Code Agent Teams** — the Orchestrator (your Claude session) spawns real Claude subagents via the `Agent` tool. Each subagent has one role and hands off immediately.
2. **Streaming multi-agent pipeline** — hotels enter the pipeline one at a time; Processor and Exporter fire simultaneously on each hotel with no batch wait.

The pattern demonstrated here applies to any domain where data arrives as a stream and each item needs to be processed, filtered, and exported independently.

---

## How It Works

```
User types one sentence
        │
        ▼
   Orchestrator (Claude)  ← CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
        │
        │   [Agent tool ×2 — parallel]
        ├── Setup Agent          → installs deps, creates folders
        │
        └── Searcher Agent       → discovers hotels, returns JSON
                │
                ▼
           Extractor Agent       → normalizes: name, price, rating, location
                │
                │   [Agent tool ×2 — parallel]
                ├── Processor Agent   → applies filters, returns passed hotels
                │
                └── Exporter Agent    → writes Excel, returns confirmation
                        │
                        ▼
                 Orchestrator sorts → prints results table
```

Key behaviors:
- **Real subagents:** Orchestrator uses the `Agent` tool — each stage is a genuine Claude instance, not a Python thread
- **Parallel spawning:** Setup + Searcher launch simultaneously; Processor + Exporter launch simultaneously
- **Streaming handoff:** Searcher → Extractor → Processor ∥ Exporter, with each hotel independent
- **Self-stopping:** pipeline halts as soon as 20 hotels are collected

---

## Two Ways to Run

### Option A — Agent Teams (the real demo)

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

Claude reads the Orchestrator Protocol from `CLAUDE.md` and spawns real Claude subagents via the `Agent` tool — Searcher, Extractor, Processor, and Exporter each run as independent Claude instances.

### Option B — tmux Live Demo (the visual demo)

Launches a 5-pane tmux session: Orchestrator on top, one colored pane per agent below. Each pane lights up in real time as its agent works.

```bash
bash scripts/run_demo.sh Bangkok 2026-06-01 2026-06-04 150 7.5 rating
```

```
┌────────────────────────────────────────────────────────────────────────┐
│  ORCHESTRATOR  (top pane)                                              │
│  Results table appears here as each hotel completes                    │
├──────────────────┬──────────────────┬──────────────────┬──────────────┤
│  SEARCHER        │  EXTRACTOR       │  PROCESSOR       │  EXPORTER    │
│  (cyan)          │  (yellow)        │  (green)         │  (magenta)   │
│  Streams hotels  │  Normalizes each │  Applies filters │  Writes Excel│
└──────────────────┴──────────────────┴──────────────────┴──────────────┘
```

---

## Quick Start

**Prerequisites:** Python 3.8+, Claude Code, tmux (for Option B)

```bash
# Install tmux (if needed)
brew install tmux

# Install Python deps
pip3 install openpyxl

# Option A: Agent Teams
claude   # then type your search request

# Option B: tmux live demo
bash scripts/run_demo.sh

# Option C: Python standalone (no Claude)
python3 scripts/pipeline.py --destination Bangkok --checkin 2026-06-01 --checkout 2026-06-04
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

| Agent | Mode | Role |
|---|---|---|
| **Orchestrator** | Claude main session | Spawns subagents via `Agent` tool, prints final table |
| **Setup** | Claude subagent | Installs deps, creates `output/`, `data/`, `data/logs/` |
| **Searcher** | Claude subagent → `scripts/search.py --agent` | Streams hotels as JSON |
| **Extractor** | Claude subagent → `scripts/extract.py` | Normalizes raw hotel batch |
| **Processor** | Claude subagent → `scripts/process.py` | Filters by price + rating |
| **Exporter** | Claude subagent → `scripts/export.py` | Writes sorted Excel |

Each script also works as a standalone CLI with JSON I/O — agents call them via Bash.

---

## Search Parameters

```python
# Agent Teams: Claude reads these from your natural-language request
# Standalone: pass as CLI args to pipeline.py

destination = "Bangkok"      # city or region
checkin     = "2026-06-01"   # ISO date
checkout    = "2026-06-04"   # ISO date
max_price   = 150.0          # USD per night
min_rating  = 7.5            # guest review score (0–10)
sort_by     = "rating"       # "rating" or "price"
max_results = 20             # stop after N hotels
```

---

## Project Structure

```
HotelAIExtractor/
├── README.md                  ← You are here
├── CLAUDE.md                  ← Agent team operating manual + Orchestrator Protocol
├── WORKSHOP_GUIDE.md          ← Step-by-step presenter guide
├── .claude/
│   └── settings.json          ← CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1, dangerouslyAllowAll: true
├── scripts/
│   ├── pipeline.py            ← Standalone Python pipeline (tmux + fallback)
│   ├── search.py              ← Searcher: streaming generator + --agent JSON CLI
│   ├── extract.py             ← Extractor: normalize hotels + --agent JSON CLI
│   ├── process.py             ← Processor: filter hotels + --agent JSON CLI
│   ├── export.py              ← Exporter: write Excel + --agent JSON CLI
│   ├── run_demo.sh            ← Launch 5-pane tmux live demo
│   └── start_agent_pane.sh    ← Per-agent pane header + tail setup
├── data/
│   ├── logs/                  ← Agent log files (tailed by tmux panes)
│   └── processed_*.json       ← Sorted JSON output
└── output/
    └── hotels_*.xlsx          ← Final Excel reports
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| AI orchestration | Claude Code + Claude Sonnet (Agent Teams) |
| Agent spawning | `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` + `Agent` tool |
| Agent instructions | `CLAUDE.md` (Orchestrator Protocol) |
| Agent CLI I/O | JSON over stdout — each script has `--agent` mode |
| Pipeline concurrency | Python `threading` + `concurrent.futures` (standalone mode) |
| Visual demo | tmux 5-pane layout with per-agent color coding |
| Data | Realistic mock hotel data (Bangkok, Singapore) |
| Export | `openpyxl` (Excel), JSON |

---

## Extending the Project

| Goal | What to change |
|---|---|
| Real hotel data | Replace `search.py` with a hotel API call |
| Different destination | Pass different `destination` in your chat message |
| Email the report | Add a Notifier agent after Exporter in the Orchestrator Protocol |
| Google Sheets output | Replace `export.py` with Sheets API calls |
| Multi-city search | Spawn one Searcher Agent per city simultaneously |
| Morning automation | Add a cron job calling `python3 scripts/pipeline.py` |
| Review sentiment | Add an Analyst agent between Extractor and Processor |

---

## Demo

See `WORKSHOP_GUIDE.md` for a complete step-by-step presenter guide including the tmux layout walkthrough, Agent Teams talking points, and common Q&A.

---

## Note on Data Source

Agoda's website uses JavaScript rendering and bot protection that blocks server-side HTTP requests. The Searcher uses realistic mock data modeled on real Bangkok and Singapore hotels. To use live data, replace `scripts/search.py` with calls to a hotel data API (e.g. RapidAPI Hotels, Expedia Affiliate Network). All other agents remain unchanged.
