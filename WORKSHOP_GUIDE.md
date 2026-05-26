# Workshop Guide: HotelAIExtractor — Streaming Multi-Agent Pipeline Demo

**Audience:** Developers, tech leads, product teams curious about AI agent orchestration  
**Duration:** 30–45 minutes  
**Goal:** Show how a team of specialized AI agents works as a streaming pipeline — each hotel processed the instant it is discovered, with Processor and Exporter running in parallel on every item

---

## What You Will See

A single natural-language request triggers a **streaming agent pipeline** that:
1. Discovers hotels one at a time as the Searcher finds them
2. Immediately normalizes each hotel via the Extractor
3. Fires Processor and Exporter **simultaneously** on each hotel — no waiting
4. Produces a formatted Excel report and a live results table

No manual coding. No forms. No confirmation prompts.

---

## The Big Idea: Why Streaming Multi-Agent?

| Batch Pipeline (old) | Streaming Pipeline (new) |
|---|---|
| Collect all 20 → then extract | Extract each hotel the moment it is found |
| Extract all → then process | Process fires immediately after extract |
| Process all → then export | Exporter runs **in parallel** with Processor |
| User waits for entire batch | Results visible as each hotel completes |
| One failure blocks everything | Each hotel is independent |

> **Key insight:** A streaming pipeline behaves like a production line — item 1 is already at the end before item 20 has even started.

---

## The Agent Team

```
┌──────────────────────────────────────────────────────────────┐
│                        ORCHESTRATOR                          │
│            (Claude — main session)                           │
│  Receives filters → spawns Setup + Pipeline → prints table   │
└──────────┬───────────────────────────────────────────────────┘
           │
     ┌─────▼──────┐      ┌──────────────────────────────────────────────┐
     │   SETUP    │      │           STREAMING PIPELINE                 │
     │   Agent    │      │                                              │
     │ Installs   │      │  [Searcher] → yields hotel_1                 │
     │ packages,  │      │                  └► [Extractor]              │
     │ creates    │      │                        └► [Processor∥Exporter│
     │ folders    │      │                                              │
     └────────────┘      │  [Searcher] → yields hotel_2 (concurrent)   │
                         │                  └► [Extractor]              │
                         │                        └► [Processor∥Exporter│
                         │                                              │
                         │  ...repeats for all 20 hotels...            │
                         │                                              │
                         │  → Final sort → Excel rewrite → Print table │
                         └──────────────────────────────────────────────┘
```

**Setup runs in parallel with the first pipeline launch.**  
**Within each hotel:** Extractor first (sequential), then Processor + Exporter simultaneously.  
**All 20 hotels** flow through the pipeline concurrently.

---

## Step-by-Step Demo Walkthrough

### Step 1 — Open the project in Claude Code

```bash
cd /Users/lloydgam/Documents/workgroup/demo/HotelAIExtractor
claude
```

> **Talking point:** "Claude Code reads `CLAUDE.md` automatically on startup. The entire agent team — their roles, rules, and pipeline order — is defined there. We don't configure anything manually."

---

### Step 2 — Show CLAUDE.md (2 min)

Open `CLAUDE.md` and walk through:
- The 5 named agents and what each one does
- The streaming pipeline flow diagram
- The "never ask, just run" rule

> **Talking point:** "This file is the operating manual for the agent team. Notice that the Processor and Exporter are marked as running in parallel — that's a deliberate architectural choice to eliminate waiting time."

---

### Step 3 — Fire the search

Paste this into Claude Code chat:

```
Search Bangkok hotels, check-in 2026-06-01, check-out 2026-06-04,
max price $150, min rating 7.5, sort by rating
```

> **Talking point:** "One sentence. No API keys, no configuration, no 'are you sure?' — it just runs."

---

### Step 4 — Watch the streaming output (the key demo moment)

Point out the live output pattern as it appears:

```
[Searcher]  Found →  Capella Bangkok            $147.0/night  ★9.5
         [Extractor] ↳ Capella Bangkok
  [Processor ∥ Exporter] ↳ Capella Bangkok
  ✓  Capella Bangkok  $147.0/night  ★9.5  Riverside

[Searcher]  Found →  Mandarin Oriental Bangkok  $135.0/night  ★9.4
         [Extractor] ↳ Mandarin Oriental Bangkok
  [Processor ∥ Exporter] ↳ Mandarin Oriental Bangkok
  ✓  Mandarin Oriental Bangkok  $135.0/night  ★9.4  Riverside
```

Narrate each line for the audience:

| Line on screen | What it means |
|---|---|
| `[Searcher] Found →` | Hotel discovered — pipeline starts immediately |
| `[Extractor] ↳` | Normalizing fields: price, rating, location |
| `[Processor ∥ Exporter] ↳` | **Both running at the same time** on this hotel |
| `✓ done` | Hotel fully processed and written to Excel |
| Next `[Searcher] Found →` | New hotel already flowing through while prior one finishes |

> **Talking point:** "Notice the Searcher is already announcing the next hotel while the previous one is still being processed. That's concurrent execution — the pipeline never idles."

---

### Step 5 — Show the final results table

After all 20 complete, the pipeline prints a sorted table directly in the terminal:

```
  #    Hotel Name                         $/night   Total     ★      Location
  ──────────────────────────────────────────────────────────────────────────
  1    Capella Bangkok                    $147.00   $441.00   9.5    Riverside
  2    Mandarin Oriental Bangkok          $135.00   $405.00   9.4    Riverside
  ...
```

> **Talking point:** "The final table is sorted by rating — that sort happens at the end after all hotels are collected, then the Excel is rewritten in order. Two phases: stream in, sort once."

---

### Step 6 — Open the Excel file

```bash
open output/hotels_Bangkok_2026-06-01.xlsx
```

Point out:
- Dark blue header row, alternating row shading
- Columns: `#`, Hotel Name, Price/Night, Total Price (3n), Rating, Location
- Exactly 20 rows, sorted by rating
- Header row frozen for scrolling

> **Talking point:** "The Exporter wrote each row as the hotel completed. The final file is a polished deliverable ready to share — no post-processing needed."

---

### Step 7 — Run a second search (optional, 5 min)

```
Search Phuket hotels, check-in 2026-07-10, check-out 2026-07-14,
max price $200, min rating 8.0, sort by price
```

> **Talking point:** "Same pipeline, different destination and filters. Nothing needs to be reconfigured — the agents are stateless and reusable."

---

## Key Demo Moments to Call Out

1. **Streaming starts immediately** — the first hotel enters the pipeline before the Searcher has found the second. No batch wait.
2. **`[Processor ∥ Exporter]`** — this line is the whole point. Two agents running simultaneously on one item.
3. **Concurrent hotels** — multiple hotels are in the pipeline at the same time (up to 8 threads).
4. **No questions asked** — Claude never pauses to confirm. The rules in `CLAUDE.md` drive behavior.
5. **Constrained output** — exactly 20 results, no more.

---

## Common Questions from the Audience

**Q: Why not just do it all in one agent?**  
A: You could. But one agent handling search + extract + process + export has a bloated context window, is hard to debug when something goes wrong, and can't run stages in parallel. Splitting by role makes each agent focused, testable, and replaceable.

**Q: What does "Processor ∥ Exporter" actually mean?**  
A: Two Python threads start at the same moment — one applying filters, one writing to Excel. They run simultaneously, so neither waits for the other.

**Q: What if the Searcher hits bot protection?**  
A: The Searcher falls back to realistic mock data and the rest of the pipeline is completely unaffected. Only one agent needs to change to support a new data source.

**Q: How do the agents share data?**  
A: Within the pipeline, data passes as Python function return values (in-memory). The final output is written to `data/` (JSON) and `output/` (Excel). No shared database, no message queue.

**Q: Can this scale to 1000 hotels?**  
A: Yes — increase `max_results` and `max_workers`. The streaming pattern means memory stays bounded; you never hold the full dataset in memory at once.

**Q: What would a real production version look like?**  
A: Replace the mock Searcher with a real hotel API (RapidAPI, Expedia API), add retry logic to each agent, and point the Exporter at a database or Google Sheets instead of Excel.

---

## File Structure Reference

```
HotelAIExtractor/
├── README.md                              ← Project overview
├── CLAUDE.md                              ← Agent team operating manual
├── WORKSHOP_GUIDE.md                      ← This file
├── .claude/
│   └── settings.json                      ← dangerouslyAllowAll: true
├── scripts/
│   ├── pipeline.py                        ← Main entry point / Orchestrator
│   ├── search.py                          ← Searcher Agent (streaming generator)
│   ├── extract.py                         ← Extractor Agent (one hotel)
│   ├── process.py                         ← Processor Agent (filter one hotel)
│   └── export.py                          ← Exporter Agent (thread-safe Excel append)
├── data/
│   └── processed_Bangkok_2026-06-01.json  ← Final sorted JSON
└── output/
    └── hotels_Bangkok_2026-06-01.xlsx     ← Final Excel report
```

---

## Closing Talking Points

- **Division of labor scales.** The same principle that makes human teams effective applies to AI agents — small, focused roles outperform generalists at scale.
- **Streaming beats batching.** Don't collect everything before starting. Process each item as it arrives.
- **Parallel at the right level.** Not everything should be parallel — Extractor must finish before Processor starts. The skill is knowing which stages can overlap.
- **`CLAUDE.md` is the team contract.** Roles, rules, and data flows are defined there. Any Claude session that opens this project knows exactly what to do.
- **Agents are composable.** Swap the Searcher for a different data source, add a Notifier agent at the end, or split the Exporter into CSV + Excel — each change is isolated.

> "This isn't just a hotel search tool. It's a reusable pattern: streaming ingestion, per-item parallel processing, and clean typed handoffs. You can apply this to any workflow where items arrive one at a time and every second of latency matters."

---

## Ideas to Show After the Demo

| Upgrade | What changes |
|---|---|
| Real hotel data (RapidAPI) | Searcher only |
| Email the report on completion | Add Notifier agent after Exporter |
| Run every morning at 7am | Add cron job calling `pipeline.py` |
| Write to Google Sheets | Replace `export.py` |
| Add review sentiment scoring | Add Analyst agent between Extractor and Processor |
| Multi-city parallel search | Spawn one pipeline per city simultaneously |
