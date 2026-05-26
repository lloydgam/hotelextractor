# Workshop Guide: HotelAIExtractor — Agent Teams + Streaming Pipeline Demo

**Audience:** Developers, tech leads, product teams curious about AI agent orchestration  
**Duration:** 30–45 minutes  
**Goal:** Show Claude Code Agent Teams in action — real Claude subagents spawned by an Orchestrator — visualized live in a 5-pane tmux layout

---

## What You Will See

Two demos, one project:

| Demo | What it shows |
|---|---|
| **tmux Live Demo** | 5 panes light up in real time — one per agent — as each hotel flows through the pipeline |
| **Agent Teams Demo** | Claude Code spawns real Claude subagents via the `Agent` tool — Searcher, Extractor, Processor, Exporter each run as independent Claude instances |

---

## The Big Picture: Agent Teams

```
User types one sentence
        │
        ▼
   Orchestrator (Claude Code session)
        │   CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
        │
        │   Agent tool ×2 — parallel
        ├─────────────────────┐
        │                     │
   [Setup Agent]        [Searcher Agent]
   installs deps        runs search.py --agent
   creates folders      returns raw hotels JSON
        │                     │
        └──────┬──────────────┘
               ▼
        [Extractor Agent]
        runs extract.py
        returns normalized JSON
               │
        Agent tool ×2 — parallel
        ├──────────────────────────┐
        │                          │
   [Processor Agent]          [Exporter Agent]
   runs process.py            runs export.py
   returns filtered JSON      writes Excel, confirms
        │
        ▼
   Orchestrator sorts → prints results table
```

> **Key point:** These are real Claude instances. The Orchestrator uses the `Agent` tool — each subagent has its own context window, runs its Bash commands, and reports back. This is not Python threading.

---

## The tmux Visual Layout

```
┌────────────────────────────────────────────────────────────────────────────┐
│  ORCHESTRATOR  (top 40%)                                                   │
│  Streaming results appear here line by line                                │
│  Final sorted table prints here when all 20 hotels complete               │
├──────────────────┬──────────────────┬──────────────────┬───────────────────┤
│  SEARCHER        │  EXTRACTOR       │  PROCESSOR       │  EXPORTER         │
│  bright cyan     │  bright yellow   │  bright green    │  bright magenta   │
│                  │                  │                  │                   │
│  ← Capella       │  ← Capella       │  ← Capella       │  ← Capella [row 1]│
│    $147/night    │    normalizing…  │    $147 ≤ $150   │    writing Excel… │
│    ★9.5          │    ✓ $147 ★9.5   │    ★9.5 ≥ ★7.5   │    ✓ row 1 written│
│                  │                  │    ✓ PASS        │                   │
└──────────────────┴──────────────────┴──────────────────┴───────────────────┘
```

Each pane tails a live log file written by the pipeline in real time. Panes update independently and simultaneously.

---

## Step-by-Step Demo Walkthrough

### Step 1 — Prerequisites (before the audience arrives)

```bash
# Install tmux if needed
brew install tmux

# Install Python dep
pip3 install openpyxl

# Verify Claude Code has Agent Teams enabled
cat .claude/settings.json | grep AGENT_TEAMS
# Should show: "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
```

---

### Step 2 — Open the project and show CLAUDE.md (3 min)

```bash
cd /Users/lloydgam/Documents/workgroup/demo/HotelAIExtractor
claude
```

Open `CLAUDE.md` and walk through two sections:

**Agent Team section:**
> "Five named agents with one role each — Orchestrator, Setup, Searcher, Extractor, Processor, Exporter. Each is a real Claude instance with its own task."

**Orchestrator Protocol section:**
> "This tells Claude exactly how to spawn the agents — which ones run in parallel (Setup + Searcher), which are sequential (Extractor), and which fire simultaneously at the end (Processor + Exporter). The protocol drives behavior — we don't configure anything manually."

---

### Step 3 — Launch the tmux live demo (the visual wow moment)

Open a terminal and run:

```bash
bash scripts/run_demo.sh Bangkok 2026-06-01 2026-06-04 150 7.5 rating
```

Or for Singapore (shows filter action — some hotels exceed $150 and are filtered out):

```bash
bash scripts/run_demo.sh Singapore 2026-06-01 2026-06-04 150 7.5 rating
```

tmux will attach automatically. You will see the 5-pane layout appear.

> **Talking point:** "Each pane is one agent. Watch them light up from left to right — Searcher finds a hotel, Extractor normalizes it, then Processor and Exporter fire simultaneously on the same hotel. The Searcher is already announcing the next hotel while the first one is still in flight."

---

### Step 4 — Narrate the live output

Point out each line as it appears:

| What you see | What to say |
|---|---|
| Searcher cyan pane: `← Capella Bangkok` | "Hotel discovered — the pipeline starts immediately, before the next hotel is found" |
| Extractor yellow pane: `normalizing fields…` | "Name, price, rating, location — cleaned and typed" |
| Processor green + Exporter magenta fire at same time | "These two run simultaneously — filtering and writing Excel at the same moment" |
| Processor: `✓ PASS` or `✗ FILTERED` | "Singapore demo is great here — watch Raffles get filtered at $350, over the $150 cap" |
| Exporter: `✓ row N written` | "Row written to Excel before the next hotel is even extracted" |
| Orchestrator top pane: final table | "All 20 hotels sorted by rating — this prints after the final sort and Excel rewrite" |

> **Talking point for Singapore:** "Raffles Hotel is $350/night — beautiful property, but over budget. The Processor catches it immediately and it never reaches the final table. The Exporter still writes it to Excel (raw data), but the final sort only includes passed hotels."

---

### Step 5 — Run Agent Teams mode in Claude Code (the conceptual wow moment)

Switch to the Claude Code chat session. Paste:

```
Search Bangkok hotels, check-in 2026-06-01, check-out 2026-06-04,
max price $150, min rating 7.5, sort by rating
```

Watch Claude use the `Agent` tool to spawn subagents. Point out:

- Claude reads the Orchestrator Protocol from `CLAUDE.md` without being told
- It spawns Setup Agent and Searcher Agent in one message (parallel)
- It waits for Searcher to return the hotel JSON
- It spawns Extractor, then spawns Processor + Exporter simultaneously
- Results come back from each agent and Orchestrator assembles the final table

> **Talking point:** "In the tmux demo, those were Python threads simulating agents. In Agent Teams mode, those are real Claude instances — each one has its own context, makes its own tool calls, and reports back. The Orchestrator is just coordinating. This is the same pattern but with actual AI agents."

---

### Step 6 — Show the Excel output

```bash
open output/hotels_Bangkok_2026-06-01.xlsx
```

Point out:
- Dark blue header row with white text
- Alternating row shading (even rows light blue)
- Columns: `#`, Hotel Name, Price/Night (USD), Total Price (3n), Rating, Location
- Exactly 20 rows, sorted by the requested field
- Header row frozen for scrolling

> **Talking point:** "The Exporter wrote each row as the hotel completed. The final file is a polished deliverable — not a raw CSV dump. This is production-ready output from a pipeline that ran in seconds."

---

### Step 7 — Optional: second search with different filters

```
Search Singapore hotels, check-in 2026-06-01, check-out 2026-06-04,
max price $150, min rating 7.5, sort by price
```

This shows:
- Filter rejection in action (Raffles, Marina Bay Sands, St. Regis all over $150)
- A new Excel file created alongside the Bangkok one
- Same pipeline, zero reconfiguration

---

## Key Demo Moments to Call Out

1. **Agent tool calls** — in Claude Code, watch the Agent tool fire twice simultaneously in Step 1 (Setup + Searcher). That's parallel agent spawning.
2. **`[Processor ∥ Exporter]`** — the clearest visual proof of parallel execution — two panes update at the same instant.
3. **Hotel filtered in real time** — Singapore's Raffles Hotel ($350) gets `✗ FILTERED` in the Processor pane immediately. No batch wait to find out it was rejected.
4. **Concurrent hotels in flight** — in the tmux demo, watch the Searcher announce hotel 3 while hotels 1 and 2 are still in Extractor. Multiple hotels are in the pipeline simultaneously.
5. **No questions asked** — Claude never pauses to confirm. The Orchestrator Protocol in `CLAUDE.md` drives all behavior.

---

## Common Questions from the Audience

**Q: What's the difference between Agent Teams and the Python pipeline?**  
A: The Python `pipeline.py` uses threads to simulate agents in one process — fast and visual for demos. Agent Teams spawns real Claude instances via the `Agent` tool. Each subagent is an independent Claude session that can use any tool (Bash, Read, Write, web search). The architecture is identical; the execution layer is different.

**Q: Why spawn real Claude subagents when Python threads are faster?**  
A: Threads share memory and can't make AI decisions. Real subagents can handle ambiguous input, choose between approaches, call external APIs, and explain what they did. As tasks get more complex ("normalize this hotel but also flag if the name looks suspicious"), an AI agent handles it; a thread can't.

**Q: Why not do it all in one agent?**  
A: One agent handling search + extract + process + export has a bloated context window, is hard to debug when something goes wrong, and can't run stages in parallel. Splitting by role makes each agent focused, testable, and replaceable.

**Q: What does `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` do?**  
A: It enables the `Agent` tool in Claude Code, which lets the main Claude session spawn and coordinate subagents. Without it, Claude can only use Bash, Read, Write, and similar single-session tools.

**Q: How do agents share data?**  
A: In Agent Teams mode, data passes as JSON strings in the agent prompts — the Orchestrator injects the Searcher's output JSON into the Extractor's prompt. In standalone Python mode, data flows as in-memory function return values. Final output goes to `data/` (JSON) and `output/` (Excel).

**Q: Can this run on real hotel data?**  
A: Yes — replace `scripts/search.py` with a real hotel API call (RapidAPI Hotels, Expedia Affiliate Network). All other agents are unchanged. The `--agent` JSON CLI interface is the only contract between the Searcher and the rest of the pipeline.

**Q: Can this scale to 1000 hotels?**  
A: In Python mode, yes — increase `max_results` and `max_workers`. The streaming pattern keeps memory bounded. In Agent Teams mode, you'd batch hotels across agents rather than one agent per hotel.

---

## File Structure Reference

```
HotelAIExtractor/
├── CLAUDE.md                              ← Agent team roles + Orchestrator Protocol
├── WORKSHOP_GUIDE.md                      ← This file
├── README.md                              ← Project overview
├── .claude/
│   └── settings.json                      ← CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
│                                             dangerouslyAllowAll: true
├── scripts/
│   ├── pipeline.py                        ← Standalone Python pipeline (tmux mode)
│   ├── search.py                          ← Searcher: generator + --agent JSON CLI
│   ├── extract.py                         ← Extractor: normalize + --agent JSON CLI
│   ├── process.py                         ← Processor: filter + --agent JSON CLI
│   ├── export.py                          ← Exporter: Excel write + --agent JSON CLI
│   ├── run_demo.sh                        ← Launch 5-pane tmux demo
│   └── start_agent_pane.sh               ← Per-pane colored header + tail
├── data/
│   ├── logs/                              ← searcher.log, extractor.log, etc.
│   └── processed_*.json                   ← Sorted JSON output
└── output/
    └── hotels_*.xlsx                      ← Final Excel reports
```

---

## Presenter Cheat Sheet

| Action | Command |
|---|---|
| tmux demo — Bangkok | `bash scripts/run_demo.sh Bangkok 2026-06-01 2026-06-04 150 7.5 rating` |
| tmux demo — Singapore (shows filtering) | `bash scripts/run_demo.sh Singapore 2026-06-01 2026-06-04 150 7.5 rating` |
| Kill tmux session | `tmux kill-session -t hotel-demo` |
| Open Claude Code | `claude` (in project root) |
| Bangkok Agent Teams prompt | `Search Bangkok hotels, check-in 2026-06-01, check-out 2026-06-04, max price $150, min rating 7.5, sort by rating` |
| Open Excel output | `open output/hotels_Bangkok_2026-06-01.xlsx` |
| Python standalone | `python3 scripts/pipeline.py --destination Bangkok --checkin 2026-06-01 --checkout 2026-06-04` |

---

## Closing Talking Points

- **Agent Teams is not a pattern for every task.** Simple scripts don't need agents. But when tasks involve judgment, ambiguity, or heterogeneous tools — real AI agents outperform threads.
- **`CLAUDE.md` is the team contract.** Roles, rules, data flows, and the Orchestrator Protocol are all there. Any Claude session that opens this project knows exactly what to do without being told.
- **Streaming beats batching.** Don't collect everything before starting. Process each item as it arrives. This applies to hotel data, customer records, documents, transactions — any stream.
- **Parallel at the right level.** Not everything should be parallel — Extractor must finish before Processor starts. The skill is knowing which stages can overlap.
- **Agents are composable.** Swap the Searcher for a different data source, add a Notifier agent, split the Exporter into CSV + database — each change is isolated to one agent.

> "This isn't just a hotel search tool. It's two reusable patterns: Claude Code Agent Teams for real AI-to-AI coordination, and streaming per-item parallel processing for zero batch wait. You can apply both to any workflow where items arrive one at a time and every second of latency matters."

---

## Ideas to Show After the Demo

| Upgrade | What changes |
|---|---|
| Real hotel data (RapidAPI) | Searcher agent only |
| Email the report on completion | Add Notifier agent to Orchestrator Protocol |
| Run every morning at 7am | Cron job calling `pipeline.py` or Claude schedule |
| Write to Google Sheets | Replace Exporter agent |
| Add review sentiment scoring | Add Analyst agent between Extractor and Processor |
| Multi-city parallel search | Spawn one Searcher Agent per city simultaneously |
| Slack notification on completion | Add Slack agent after Exporter |
