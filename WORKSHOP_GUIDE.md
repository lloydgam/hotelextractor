# Workshop Guide: Hotel AI Extractor — Multi-Agent Demo

**Audience:** Developers, tech leads, product teams curious about AI agent orchestration  
**Duration:** 30–45 minutes  
**Goal:** Demonstrate how a team of specialized AI agents collaborates to complete a real-world task — no manual coding, no back-and-forth prompting

---

## What You Will See

A single natural-language request triggers a **coordinated team of AI agents** that:
1. Set up the environment automatically
2. Search Agoda for hotels matching your filters
3. Extract and structure the raw data
4. Filter, sort, and clean the results
5. Export a formatted Excel report — all in one run

---

## The Big Idea: Why Multi-Agent?

| Single Agent | Agent Team |
|---|---|
| One agent does everything | Each agent has one job |
| Sequential, slow | Parallel where possible |
| Hard to debug | Easy to isolate failures |
| Context gets overloaded | Each agent has clean context |
| Doesn't scale | Add agents as complexity grows |

> **Key insight:** Just like a real team, agents work better when they have a clear role, a specific input, and a defined output.

---

## Meet the Agent Team

```
┌─────────────────────────────────────────────────────┐
│                    ORCHESTRATOR                     │
│         (Claude — main session / you)               │
│   Receives filters → delegates → collects results   │
└──────────┬──────────────────────┬───────────────────┘
           │                      │
     ┌─────▼──────┐        ┌──────▼──────┐
     │   SETUP    │        │  SEARCHER   │
     │   Agent    │        │   Agent     │
     │ Installs   │        │ Queries     │
     │ packages,  │        │ Agoda,      │
     │ creates    │        │ collects    │
     │ folders    │        │ raw data    │
     └────────────┘        └──────┬──────┘
                                  │
                           ┌──────▼──────┐
                           │  EXTRACTOR  │
                           │   Agent     │
                           │ Parses HTML │
                           │ pulls name, │
                           │ price, etc. │
                           └──────┬──────┘
                                  │
                           ┌──────▼──────┐
                           │  PROCESSOR  │
                           │   Agent     │
                           │ Filters,    │
                           │ dedupes,    │
                           │ sorts top20 │
                           └──────┬──────┘
                                  │
                           ┌──────▼──────┐
                           │  EXPORTER   │
                           │   Agent     │
                           │ Writes .xlsx│
                           │ prints table│
                           └─────────────┘
```

**Setup + Searcher run in parallel.**  
**Extractor → Processor → Exporter run sequentially** (each needs the prior output).

---

## Step-by-Step Demo Walkthrough

### Step 1 — Open the project in Claude Code

```bash
cd /Users/lloydgam/Documents/workgroup/demo/HotelAIExtractor
claude
```

> **Talking point:** Claude Code reads `CLAUDE.md` automatically. The agent team architecture, rules, and output format are all defined there — no prompting tricks needed.

---

### Step 2 — Show the CLAUDE.md (1 min)

Open `CLAUDE.md` and walk through:
- The 5 named agents and their roles
- The execution flow diagram
- The "never ask, just run" rule

> **Talking point:** "This file is the team's operating manual. Any time Claude picks up this project, it knows exactly who does what."

---

### Step 3 — Fire the first search request

Paste this into Claude Code chat:

```
Search Bangkok hotels, check-in 2026-06-01, check-out 2026-06-04,
max price $150, min rating 7.5, sort by rating
```

> **Talking point:** "One sentence. No forms, no API keys to configure, no code to write. Watch what happens next."

**What to watch for:**
- Claude spawns Setup Agent and Searcher Agent simultaneously (parallel)
- You will see two agents running at the same time in the output
- Once raw data is collected, Extractor kicks off automatically
- Then Processor, then Exporter — each agent handing off to the next

---

### Step 4 — Observe agent handoffs (live)

As the run progresses, narrate what the audience is seeing:

| What appears on screen | What it means |
|---|---|
| Two agents launch at the same time | Parallel execution — Setup + Searcher |
| "Raw data saved to `data/`" | Searcher Agent completed its job |
| "Extracting fields..." | Extractor Agent received the handoff |
| "Filtered to 20 results, sorted by rating" | Processor Agent ran |
| Table printed in chat | Exporter Agent finished — results ready |

---

### Step 5 — Show the output

Open the Excel file:

```bash
open output/hotels_Bangkok_2026-05-26.xlsx
```

Point out:
- Column structure: Hotel Name, Price, Rating, Location
- Sorted as requested
- Exactly 20 rows — no more

> **Talking point:** "The agent stopped at 20. It didn't keep scraping forever. The rules in CLAUDE.md constrain its behavior — the team follows the playbook."

---

### Step 6 — Run a second search with different filters (optional, 5 min)

Change the destination and sort order to show repeatability:

```
Search Phuket hotels, check-in 2026-07-10, check-out 2026-07-14,
max price $200, min rating 8.0, sort by price, resort only
```

> **Talking point:** "Same team, different task. The agents are reusable — they don't need to be re-configured between runs."

---

## Key Demo Moments (Highlight These for the Audience)

1. **Parallel launch** — Two agents start at the exact same time. Point this out explicitly.
2. **No questions asked** — Claude never says "should I proceed?" — it just runs.
3. **Clean handoffs** — Each agent reads from `data/`, writes to `data/`, passes the baton.
4. **Constrained behavior** — Stops at 20. Respects max price. Follows the playbook.
5. **Repeatable** — Run it again with different params, same clean result.

---

## Common Questions from the Audience

**Q: Could one agent do all of this?**  
A: Yes, but it would be slower, harder to debug, and the context window would fill up with irrelevant details. Specialization makes each agent faster and more reliable.

**Q: What if the Searcher fails?**  
A: Only the Searcher needs to retry — Extractor, Processor, and Exporter are unaffected. Isolation makes failures cheaper to fix.

**Q: How do agents communicate?**  
A: Through files (`data/` folder) and return values. Each agent writes structured output that the next agent reads. No shared memory, no tight coupling.

**Q: Can we add more agents?**  
A: Yes. You could add a Price History Agent, a Review Sentiment Agent, or a Booking Link Agent — each plugs into the pipeline at the right stage.

**Q: What is the Orchestrator doing while agents run?**  
A: Monitoring, collecting results, and deciding what to spawn next. It's the team lead, not a worker.

---

## Folder Structure Reference

```
HotelAIExtractor/
├── CLAUDE.md                          ← Agent team operating manual
├── WORKSHOP_GUIDE.md                  ← This file
├── scripts/                           ← Reusable Python scripts per agent
│   ├── search.py
│   ├── extract.py
│   ├── process.py
│   └── export.py
├── data/                              ← Raw + intermediate data
│   ├── raw_Bangkok_2026-05-26.json
│   └── extracted_Bangkok_2026-05-26.json
└── output/                            ← Final Excel reports
    └── hotels_Bangkok_2026-05-26.xlsx
```

---

## Closing Talking Points

- **Multi-agent = division of labor.** The same principle that makes human teams effective applies to AI.
- **CLAUDE.md is the team contract.** Define roles, rules, and output formats there — the agents follow it every time.
- **Parallel where possible, sequential where necessary.** This is the architecture decision that determines speed.
- **Agents are composable.** You can swap out, upgrade, or add agents without rewriting the whole system.

> "This is not just a hotel scraper. It's a pattern you can apply to any workflow that has distinct stages, multiple data sources, or repetitive tasks."

---

## Next Steps to Show After the Demo

- Swap Agoda for another source (Booking.com, Expedia) — only the Searcher changes
- Add a Slack/email notification agent at the end
- Schedule it to run every morning automatically
- Connect to a dashboard instead of Excel
