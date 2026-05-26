# Workshop Guide: HotelAIExtractor — Claude Code Agent Teams

**Audience:** Developers, tech leads, product teams curious about AI agent orchestration  
**Duration:** 30–45 minutes  
**Goal:** Show Claude Code Agent Teams in action — an Orchestrator spawning real Claude subagents that coordinate, hand off data, and run in parallel

---

## What You Will See

One natural-language request triggers a coordinated team of real Claude agents:

- Orchestrator spawns **Setup** and **Searcher** simultaneously via the `Agent` tool
- Searcher returns hotels as JSON; Orchestrator passes it to **Extractor**
- Extractor normalizes the data; Orchestrator spawns **Processor** and **Exporter** simultaneously
- Results flow back, Orchestrator sorts and prints the final table

No scripts are run manually. No configuration. Claude reads `CLAUDE.md`, follows the Orchestrator Protocol, and coordinates the team.

---

## The Agent Team

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
   installs deps        discovers hotels
   creates folders      returns raw JSON
        │                     │
        └──────┬──────────────┘
               ▼
        [Extractor Agent]
        normalizes each record
        returns clean JSON
               │
        Agent tool ×2 — parallel
        ├──────────────────────────┐
        │                          │
   [Processor Agent]          [Exporter Agent]
   applies filters             writes Excel
   returns passed hotels       confirms rows written
        │
        ▼
   Orchestrator sorts → prints results table
```

Each subagent is a real Claude instance with its own context window. It receives a task, uses Bash to run its work, and reports back to the Orchestrator.

---

## The tmux Architecture View

Before running the Agent Teams demo, this visualization helps the audience understand what each role does:

```
┌────────────────────────────────────────────────────────────────────────────┐
│  ORCHESTRATOR  (top 40%)                                                   │
│  Coordinates the team — spawns agents, assembles results, prints table     │
├──────────────────┬──────────────────┬──────────────────┬───────────────────┤
│  SEARCHER        │  EXTRACTOR       │  PROCESSOR       │  EXPORTER         │
│  bright cyan     │  bright yellow   │  bright green    │  bright magenta   │
│                  │                  │                  │                   │
│  Discovers hotels│  Normalizes each │  Applies filters │  Writes to Excel  │
│  one at a time   │  record          │  price + rating  │  row by row       │
└──────────────────┴──────────────────┴──────────────────┴───────────────────┘
```

```bash
# Launch the architecture visualization (Bangkok)
bash scripts/run_demo.sh Bangkok 2026-06-01 2026-06-04 150 7.5 rating

# Or Singapore — shows the Processor filtering over-budget hotels in real time
bash scripts/run_demo.sh Singapore 2026-06-01 2026-06-04 150 7.5 rating
```

> **Talking point:** "Each pane is one agent role. In Agent Teams, these are real Claude instances — each one receives a task, runs its tools, and reports back to the Orchestrator."

---

## Step-by-Step Demo Walkthrough

### Step 1 — Prerequisites (before the audience arrives)

```bash
# Install tmux if needed
brew install tmux

# Install Python dep
pip3 install openpyxl

# Verify Agent Teams is enabled
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
> "Six named roles — Orchestrator, Setup, Searcher, Extractor, Processor, Exporter. Each is a real Claude instance with one job."

**Orchestrator Protocol section:**
> "This is the contract that drives all behavior. It tells Claude exactly when to use the Agent tool, which agents run in parallel, and what JSON each one passes to the next. We don't configure anything manually — the protocol does it."

---

### Step 3 — Optional: show the tmux architecture view (2 min)

Open a second terminal and run the tmux layout so the audience can see the roles visually while you run the Agent Teams demo.

```bash
bash scripts/run_demo.sh Bangkok 2026-06-01 2026-06-04 150 7.5 rating
```

Leave it running as a visual reference. Then switch back to Claude Code.

---

### Step 4 — Fire the Agent Teams demo (the main event)

In the Claude Code chat, paste:

```
Search Bangkok hotels, check-in 2026-06-01, check-out 2026-06-04,
max price $150, min rating 7.5, sort by rating
```

Watch Claude use the `Agent` tool. Call out each moment as it happens:

| What Claude does | What to say |
|---|---|
| Spawns Setup + Searcher simultaneously | "Two Agent tool calls in one message — that's parallel agent spawning" |
| Waits for Searcher to return JSON | "The Orchestrator is blocked here — it needs the hotel list before it can continue" |
| Spawns Extractor with Searcher's JSON | "Data passes as JSON in the agent prompt — no shared memory, no database" |
| Spawns Processor + Exporter simultaneously | "Again, two agents at once — filtering and Excel writing happen at the same moment" |
| Prints the final sorted table | "Orchestrator assembles the result — sorted by rating, exactly 20 hotels" |

> **Talking point:** "Notice Claude never asked a single question. The Orchestrator Protocol in `CLAUDE.md` defines the entire workflow. One sentence in, full results out."

---

### Step 5 — Singapore: show the Processor filtering in action (optional, 5 min)

```
Search Singapore hotels, check-in 2026-06-01, check-out 2026-06-04,
max price $150, min rating 7.5, sort by price
```

Point out what the Processor agent returns — Raffles ($350), Marina Bay Sands ($280), and St. Regis ($220) are all rejected before they reach the final table.

> **Talking point:** "The Processor is a real Claude agent making filter decisions. You could make this logic as complex as you want — 'flag hotels with fewer than 100 reviews' or 'exclude properties undergoing renovation' — and the Processor handles it without changing any other agent."

---

### Step 6 — Show the Excel output

```bash
open output/hotels_Bangkok_2026-06-01.xlsx
```

Point out:
- Dark blue header row, alternating row shading, frozen top row
- Columns: `#`, Hotel Name, Price/Night (USD), Total Price (3n), Rating, Location
- 20 rows, sorted by the requested field
- Written by the Exporter agent — the Orchestrator never touches the file directly

> **Talking point:** "The Exporter agent owns the file. If you wanted to write to Google Sheets instead, you replace that one agent. Nothing else changes."

---

## Key Demo Moments to Call Out

1. **Parallel Agent spawning** — watch the `Agent` tool fire twice in one message (Setup + Searcher, then Processor + Exporter). The two agents run simultaneously and both report back before the Orchestrator continues.
2. **JSON handoff** — the Searcher's raw hotel JSON becomes the Extractor's input. The Extractor's normalized JSON becomes the Processor's and Exporter's input. Clean typed handoffs between real agents.
3. **Processor filtering** — Singapore makes this vivid. Raffles is $350/night and gets cut. The Orchestrator's final table only shows hotels the Processor approved.
4. **No human in the loop** — from one sentence to a formatted Excel file, Claude coordinates the entire team without asking a single clarifying question.
5. **`CLAUDE.md` as the team contract** — point to it. Every behavior — parallel spawning, JSON format, sort order, stop at 20 — is defined there.

---

## Common Questions from the Audience

**Q: Why not do it all in one agent?**  
A: One agent handling search + extract + process + export has a bloated context window, mixes concerns, and can't run stages in parallel. Splitting by role makes each agent focused, testable, and replaceable independently.

**Q: What does `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` do?**  
A: It enables the `Agent` tool in Claude Code, allowing the main session to spawn and coordinate subagents. Each subagent is a full Claude instance with its own tools and context.

**Q: How do agents share data?**  
A: As JSON strings passed in the agent prompt. The Orchestrator injects the previous agent's output into the next agent's task. No shared database, no message queue — just clean JSON handoffs.

**Q: Can I swap out one agent without changing the others?**  
A: Yes — that's the whole point. Replace the Searcher with a live hotel API, the Exporter with Google Sheets, or add a Notifier agent at the end. Each change is isolated to one agent. The Orchestrator Protocol defines the contract between them.

**Q: Can this run on real hotel data?**  
A: Replace `scripts/search.py` with a real hotel API call (RapidAPI Hotels, Expedia Affiliate Network). The Searcher agent calls it via Bash and returns the same JSON schema. Every other agent is unchanged.

**Q: What happens if an agent fails?**  
A: The Orchestrator receives the failure in the agent's response and can decide how to handle it — retry, skip, or surface the error. Because agents are isolated, one failure doesn't corrupt the others.

---

## File Structure Reference

```
HotelAIExtractor/
├── CLAUDE.md                              ← Agent team roles + Orchestrator Protocol
├── WORKSHOP_GUIDE.md                      ← This file
├── README.md                              ← Project overview
├── .claude/
│   └── settings.json                      ← CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
├── scripts/
│   ├── search.py                          ← Searcher agent tool (--agent JSON mode)
│   ├── extract.py                         ← Extractor agent tool (--agent JSON mode)
│   ├── process.py                         ← Processor agent tool (--agent JSON mode)
│   ├── export.py                          ← Exporter agent tool (--agent JSON mode)
│   ├── run_demo.sh                        ← tmux architecture visualization
│   └── start_agent_pane.sh               ← Per-pane colored header
├── data/
│   └── processed_*.json                   ← Sorted JSON output
└── output/
    └── hotels_*.xlsx                      ← Final Excel reports
```

---

## Presenter Cheat Sheet

| Action | Command |
|---|---|
| Open Claude Code | `claude` (in project root) |
| Bangkok prompt | `Search Bangkok hotels, check-in 2026-06-01, check-out 2026-06-04, max price $150, min rating 7.5, sort by rating` |
| Singapore prompt (shows filtering) | `Search Singapore hotels, check-in 2026-06-01, check-out 2026-06-04, max price $150, min rating 7.5, sort by price` |
| tmux architecture view — Bangkok | `bash scripts/run_demo.sh Bangkok 2026-06-01 2026-06-04 150 7.5 rating` |
| tmux architecture view — Singapore | `bash scripts/run_demo.sh Singapore 2026-06-01 2026-06-04 150 7.5 rating` |
| Kill tmux session | `tmux kill-session -t hotel-demo` |
| Open Excel output | `open output/hotels_Bangkok_2026-06-01.xlsx` |

---

## Closing Talking Points

- **`CLAUDE.md` is the team contract.** Roles, data flows, parallel steps, and handoff formats are all defined there. Any Claude Code session that opens this project knows exactly what to do without being told.
- **Parallel at the right level.** Not everything should run simultaneously — Extractor must finish before Processor starts. The Orchestrator Protocol defines exactly which stages overlap and which are sequential.
- **Agents are composable.** Swap one agent, add a new one, split an existing one — each change is isolated. The Orchestrator Protocol is the only thing that coordinates them.
- **This pattern scales to any domain.** Hotel search today. Customer onboarding, document processing, data enrichment, report generation tomorrow. Anywhere you have a multi-step workflow with distinct roles and typed handoffs.

> "The hotel is just the use case. What this actually demonstrates is a pattern: an Orchestrator that coordinates a team of specialized agents, with parallel execution at the right stages and clean JSON handoffs between them. That pattern applies everywhere."

---

## Ideas to Show After the Demo

| Upgrade | What changes |
|---|---|
| Real hotel data (RapidAPI) | Searcher agent only |
| Email the report on completion | Add Notifier agent to Orchestrator Protocol |
| Write to Google Sheets | Replace Exporter agent |
| Add review sentiment scoring | Add Analyst agent between Extractor and Processor |
| Multi-city parallel search | Spawn one Searcher Agent per city simultaneously |
| Slack notification on completion | Add Slack agent after Exporter |
| Schedule it daily | Claude Code `/schedule` — runs the whole Agent Teams pipeline on a cron |
