# Workshop Guide: HotelAIExtractor — Claude Code Agent Teams

**Audience:** Developers, tech leads, product teams curious about AI agent orchestration  
**Duration:** 30–45 minutes  
**Goal:** Show Claude Code Agent Teams in action — a lead session creating full Claude Code teammates that share a task list, communicate through files, and run parallel stages

---

## What You Will See

One natural-language request causes the lead Claude session to:

1. Create a 4-teammate agent team (searcher, extractor, processor, exporter)
2. Set up a task list with dependencies
3. Each teammate claims its task when dependencies clear — `process` and `export` unblock simultaneously when `extract` finishes
4. Teammates communicate through files in `data/` — no data passes through the lead
5. Lead reads the final results, sorts, and prints the table

In tmux (`"teammateMode": "tmux"` is set), each teammate appears in its own pane. You can press `Shift+Down` to visit any teammate's session directly.

---

## Agent Teams vs Subagents — Know the Difference

The docs draw a hard line between these two patterns. This project uses **Agent Teams**.

| | Subagents | **Agent Teams** ← this project |
|---|---|---|
| What they are | Workers spawned inside the main session | Separate full Claude Code sessions |
| Communication | Report back to main agent only | Teammates message each other; share task list |
| Coordination | Main agent manages everything | Shared task list — teammates self-claim work |
| Display | No dedicated terminal | Each teammate gets its own tmux pane |
| Task dependencies | None — main agent decides order | Built-in: blocked tasks unblock automatically |
| Best for | Sequential focused tasks | Parallel stages, independent roles |

---

## The Team Architecture

```
Lead (Orchestrator Claude Code session)
│   Creates team → sets up task list → monitors → finalizes
│
├── [search task]   ─── searcher teammate
│       │
│       └── unblocks ──► [extract task] ─── extractor teammate
│                               │
│                               └── unblocks both simultaneously:
│                                       │
│                    ┌──────────────────┴──────────────────┐
│               [process task]                       [export task]
│               processor teammate                  exporter teammate
│               writes processed JSON               writes Excel
│                    │                                    │
│                    └────────────────┬───────────────────┘
│                                     │
└── Lead reads processed JSON, sorts, prints table
```

**File handoffs between teammates:**
```
data/raw_{dest}_{date}.json         ← searcher writes
data/extracted_{dest}_{date}.json   ← extractor writes; processor + exporter read
data/processed_{dest}_{date}.json   ← processor writes
output/hotels_{dest}_{date}.xlsx    ← exporter writes
```

---

## Step-by-Step Demo Walkthrough

### Step 1 — Prerequisites (before the audience arrives)

```bash
pip3 install openpyxl

# Verify Agent Teams is enabled
cat .claude/settings.json | grep -E "AGENT_TEAMS|teammateMode"
# Should show:
#   "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
#   "teammateMode": "tmux"
```

Start a tmux session so teammates get their own panes automatically:

```bash
tmux new-session -s demo
cd /Users/lloydgam/Documents/workgroup/demo/HotelAIExtractor
claude
```

---

### Step 2 — Show CLAUDE.md (3 min)

Open `CLAUDE.md` and walk through:

**Agent Team section:**
> "Five roles — Lead, Searcher, Extractor, Processor, Exporter. Each teammate is a full Claude Code session. The Lead creates the team and never does the work itself."

**Orchestrator Protocol — task list:**
> "Look at the task dependencies: `process` and `export` both depend on `extract` but not on each other. That dependency graph is what causes them to run in parallel automatically — the task list enforces it, not the Lead."

**File handoffs:**
> "Teammates don't pass data through the Lead. Searcher writes a file. Extractor reads it and writes its own. Processor and Exporter both read the extracted file and write their outputs. Clean, auditable, no context bloat."

---

### Step 3 — Fire the demo (the main event)

In Claude Code chat:

```
Search Bangkok hotels, check-in 2026-06-01, check-out 2026-06-04,
max price $150, min rating 7.5, sort by rating
```

Watch the team come to life. Call out each moment:

| What happens | What to say |
|---|---|
| Lead creates the team | "It reads the Orchestrator Protocol from `CLAUDE.md` — no manual setup" |
| Task list appears | "Four tasks with dependencies — `process` and `export` are blocked until `extract` finishes" |
| New tmux panes open | "Each teammate is a real Claude Code session. You can click into any pane" |
| Searcher claims `search` | "It runs `search.py`, writes `data/raw_Bangkok_2026-06-01.json`, marks the task done" |
| `extract` unblocks, Extractor claims it | "Task dependency resolved automatically — Lead didn't intervene" |
| `process` AND `export` unblock simultaneously | "Both tasks were waiting on `extract`. The moment it completes, both teammates wake up and start" |
| Processor and Exporter panes both active at once | "Two Claude Code sessions running in parallel, each with its own context window" |
| Lead prints the final table | "Lead reads the processed file, sorts, formats, done" |

---

### Step 4 — Show what teammates can see

Press `Shift+Down` to cycle through teammate panes. Point out:

- Each pane is a full Claude Code session — it loaded `CLAUDE.md` on startup
- You can type directly into a teammate's pane to redirect it
- The shared task list is visible to all teammates — they coordinate without the Lead

> **Talking point:** "This is the key difference from subagents. With subagents, every message goes through the Lead. Here, Processor and Exporter are running simultaneously in their own sessions — they don't talk to the Lead until they're done. If Extractor needed to warn the Processor about something, it could message it directly."

---

### Step 5 — Singapore: show the Processor filtering (optional, 5 min)

```
Search Singapore hotels, check-in 2026-06-01, check-out 2026-06-04,
max price $150, min rating 7.5, sort by price
```

The Processor teammate filters out Raffles ($350), Marina Bay Sands ($280), and St. Regis ($220). Watch `data/processed_Singapore_2026-06-01.json` have fewer entries than `data/extracted_Singapore_2026-06-01.json`.

> **Talking point:** "The Processor wrote its output to a file. You can open `data/processed_Singapore_2026-06-01.json` right now and inspect exactly what it decided and why — full auditability. Every teammate's output is a file."

---

### Step 6 — Open the Excel output

```bash
open output/hotels_Bangkok_2026-06-01.xlsx
```

- Dark blue header, alternating shading, frozen top row
- Sorted by the field you requested
- Written by the Exporter teammate — the Lead never touched the file directly

---

## Key Demo Moments to Call Out

1. **Task list with dependencies** — the `process` and `export` tasks are visually blocked, then unblock simultaneously when `extract` completes. Dependency enforcement is automatic.
2. **Parallel tmux panes** — Processor and Exporter panes both become active at the same instant. Two real Claude sessions, simultaneous.
3. **File trail in `data/`** — after the run, open `data/`. Four files, one per stage. Each teammate's work is fully auditable.
4. **`Shift+Down` into a teammate** — show the audience that each pane is a live Claude Code session. Type a question to a teammate directly.
5. **Lead never handles the data** — the Lead sets up the team and prints the final table. It never reads or passes hotel JSON. Teammates hand off between themselves through files.

---

## Common Questions from the Audience

**Q: What's the difference between Agent Teams and subagents?**  
A: Subagents spawn inside the main session and only report back to it. Agent Teams creates full separate Claude Code sessions as teammates. Teammates share a task list, can message each other directly, and each has its own tmux pane. The task dependency system is what makes parallel stages work automatically.

**Q: Why use files for handoffs instead of passing data in messages?**  
A: Files keep the Lead's context lean — no large JSON blobs accumulating. They're also auditable: after the run, you can inspect exactly what every teammate produced. And they're natural for Claude Code sessions, which already work with the filesystem.

**Q: What does `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` do?**  
A: Enables the Agent Teams feature in Claude Code. Without it, only the single-session tools are available. With it, the Lead can create a team, set up a task list, and spawn teammates as full Claude Code sessions.

**Q: What does `"teammateMode": "tmux"` do?**  
A: Forces split-pane mode — each teammate gets its own tmux pane regardless of whether you started inside tmux. Without it, the default is "auto" (split panes only if already in tmux; otherwise in-process with `Shift+Down` to cycle).

**Q: Can teammates message each other?**  
A: Yes — that's a core Agent Teams feature. In this pipeline they don't need to (the file handoffs are sufficient), but if Extractor found malformed data it could warn Processor directly before Processor even starts.

**Q: Can I swap one teammate without changing the others?**  
A: Yes. Each teammate's contract is its input and output file schema. Replace the Searcher with a live hotel API, and as long as it writes the same `raw_*.json` schema, every downstream teammate is unchanged.

**Q: What if a task gets stuck?**  
A: Press `Shift+Down` to visit the teammate's pane directly. You can type additional instructions, redirect it, or ask the Lead to reassign the task. The docs note that task status can sometimes lag — if a task looks stuck but the work is done, you can update it manually.

---

## File Structure Reference

```
HotelAIExtractor/
├── CLAUDE.md                              ← Agent team roles + Orchestrator Protocol
├── WORKSHOP_GUIDE.md                      ← This file
├── README.md                              ← Project overview
├── .claude/
│   └── settings.json                      ← CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1
│                                             teammateMode: tmux
├── scripts/
│   ├── search.py                          ← Searcher tool  (--output writes file)
│   ├── extract.py                         ← Extractor tool (--input / --output)
│   ├── process.py                         ← Processor tool (--input / --output)
│   └── export.py                          ← Exporter tool  (--input reads file)
├── data/
│   ├── raw_*.json                         ← Searcher output
│   ├── extracted_*.json                   ← Extractor output
│   └── processed_*.json                   ← Processor output
└── output/
    └── hotels_*.xlsx                      ← Final Excel report
```

---

## Presenter Cheat Sheet

| Action | Command / Key |
|--------|---------------|
| Start tmux + Claude Code | `tmux new-session -s demo` then `claude` |
| Bangkok search | `Search Bangkok hotels, check-in 2026-06-01, check-out 2026-06-04, max price $150, min rating 7.5, sort by rating` |
| Singapore search (shows filtering) | `Search Singapore hotels, check-in 2026-06-01, check-out 2026-06-04, max price $150, min rating 7.5, sort by price` |
| Cycle through teammate panes | `Shift+Down` |
| Open Excel output | `open output/hotels_Bangkok_2026-06-01.xlsx` |
| Inspect file trail | `ls -la data/` |
| Kill tmux session | `tmux kill-session -t demo` |

---

## Closing Talking Points

- **`CLAUDE.md` is the team contract.** The Orchestrator Protocol defines teammate roles, task dependencies, file schemas, and what the Lead does at the end. Any Claude Code session that opens this project knows exactly what team to create.
- **Task dependencies do the coordination.** The Lead doesn't check whether Extractor is done before signaling Processor — the task list handles it. This is how Agent Teams scales: add more tasks, add more teammates, the dependency graph routes work automatically.
- **File handoffs are the communication layer.** Teammates don't need a message broker or shared memory. They write files, read files, and the filesystem is the bus. Auditable, debuggable, simple.
- **This pattern scales to any domain.** Parallel PR review (security + performance + tests), competing bug hypotheses, cross-layer feature work (frontend + backend + tests as separate teammates), multi-city data pipelines. Anywhere you have independent roles with clear output contracts.

> "What this demonstrates is the Agent Teams primitive: a lead that creates a team, a task list that enforces dependencies, and teammates that are real Claude sessions. The hotel is just the domain. The pattern is what you take home."

---

## Build Your Own SDLC Agent Team

HotelAIExtractor is a template. This section shows how to transfer every concept — task list, file handoffs, parallel stages — directly into software development workflows.

### Pattern mapping

| HotelAIExtractor concept | SDLC equivalent |
|--------------------------|-----------------|
| Lead (Orchestrator) | Creates the team, monitors the task list, synthesizes the result |
| Searcher teammate | Issue analyst, ticket reader, codebase explorer |
| Extractor teammate | Spec writer, impact mapper, plan generator |
| Processor teammate | Code reviewer, quality gate, security auditor |
| Exporter teammate | Implementer, PR creator, doc writer |
| `data/raw_*.json` | `analysis/findings.md` — raw discovery |
| `data/extracted_*.json` | `specs/plan.md` — normalized work plan |
| `data/processed_*.json` | `review/approved.md` — gated output |
| `output/hotels_*.xlsx` | Commit, PR, or release artifact |
| `process` ∥ `export` | Any two teammates with the same dependency but no dependency on each other |

---

### Team Template 1: PR Code Review

Three reviewers with distinct lenses, all running in parallel. Lead synthesizes.

**Teammates:** security-reviewer, performance-reviewer, test-reviewer

**Task list:**
```
[security-review]     → security-reviewer      (no deps)   ┐
[performance-review]  → performance-reviewer   (no deps)   ├─ all parallel
[test-review]         → test-reviewer          (no deps)   ┘
[synthesize]          → lead                   (depends: all three)
```

**File handoffs:**
```
review/security.md      ← security-reviewer writes
review/performance.md   ← performance-reviewer writes
review/tests.md         ← test-reviewer writes
review/summary.md       ← lead writes (synthesized)
```

**CLAUDE.md Orchestrator Protocol snippet:**
```
Create a PR review team with 3 teammates: security-reviewer, performance-reviewer, test-reviewer.

Tasks (all parallel, no dependencies):
- [security-review]:     Read the PR diff, audit for vulnerabilities, write review/security.md
- [performance-review]:  Read the PR diff, flag performance regressions, write review/performance.md
- [test-review]:         Read the PR diff, assess coverage gaps, write review/tests.md

After all three complete: read their output files and write a synthesized review/summary.md.
Post the summary as a PR comment.
```

---

### Team Template 2: Feature Implementation

Analyst first, then implementer and test-writer in parallel, reviewer last.

**Teammates:** analyst, implementer, test-writer, reviewer

**Task list:**
```
[explore]    → analyst      (no deps)
[implement]  → implementer  (depends: explore)   ┐
[test]       → test-writer  (depends: explore)   ┘ parallel
[review]     → reviewer     (depends: implement)
```

**File handoffs:**
```
analysis/findings.md    ← analyst writes     (codebase map, affected files, risks)
src/                    ← implementer writes  (code changes)
tests/                  ← test-writer writes  (new/updated tests)
review/feedback.md      ← reviewer writes     (quality gate)
```

**CLAUDE.md Orchestrator Protocol snippet:**
```
Create a feature team with 4 teammates: analyst, implementer, test-writer, reviewer.

Tasks:
- [explore]:    Read the ticket and codebase. Write analysis/findings.md with: affected files,
                suggested approach, risks. No code changes.
- [implement]:  Read analysis/findings.md. Write the code changes. (depends: explore)
- [test]:       Read analysis/findings.md. Write tests for the new behavior. (depends: explore)
- [review]:     Read the code changes in src/. Write review/feedback.md with pass/fail verdict. 
                (depends: implement)

After all tasks complete: if review passes, create the PR. If not, ask implementer to address feedback.
```

> **Workshop talking point:** "The analyst and implementer are sequential — you can't implement before you understand the problem. But test-writer and implementer are parallel — tests are written from the spec, not from the code. Same pattern as `process` ∥ `export` in the hotel pipeline."

---

### Team Template 3: Bug Investigation (Competing Hypotheses)

Multiple teammates investigate different theories simultaneously. The one that survives is the root cause.

**Teammates:** hypothesis-network, hypothesis-state, hypothesis-concurrency (or name them after your theories)

**Task list:**
```
[investigate-network]     → hypothesis-network      (no deps)  ┐
[investigate-state]       → hypothesis-state        (no deps)  ├─ all parallel
[investigate-concurrency] → hypothesis-concurrency  (no deps)  ┘
```

Teammates can message each other directly to challenge findings as they work.

**File handoffs:**
```
debug/network-findings.md      ← hypothesis-network writes
debug/state-findings.md        ← hypothesis-state writes
debug/concurrency-findings.md  ← hypothesis-concurrency writes
```

**CLAUDE.md Orchestrator Protocol snippet:**
```
Create a bug investigation team with 3 teammates. Each investigates a different root cause theory
for [the bug]. Have them message each other to challenge each other's findings as they work.

Teammates:
- hypothesis-network:     Investigate network/timeout issues. Write debug/network-findings.md.
- hypothesis-state:       Investigate shared state / race conditions. Write debug/state-findings.md.
- hypothesis-concurrency: Investigate thread safety. Write debug/concurrency-findings.md.

After all complete: read findings, identify which theory has the strongest evidence, implement the fix.
```

> **Workshop talking point:** "The docs specifically call out the competing-hypothesis pattern as one of the strongest Agent Teams use cases. A single investigator anchors on the first plausible theory. Teammates actively trying to disprove each other converge on the real root cause faster."

---

### The Three Rules for Designing Any SDLC Team

**Rule 1: One teammate, one concern.**
Never give a teammate two jobs. Analyst does not write code. Reviewer does not run tests. Small, focused roles are easier to redirect and replace.

**Rule 2: Draw the dependency graph before writing the protocol.**
Ask: "What can run before I have X?" If two tasks share a dependency but don't depend on each other — like test-writer and implementer both depending on analyst — they run in parallel. Draw it out, then write the task list.

**Rule 3: Files are the API between teammates.**
Decide the output file for each teammate before you write their instructions. The file is the contract. Any teammate that consumes it reads that file path — not a message, not a return value. This keeps context lean and makes every handoff auditable.

---

## Ideas to Show After the Demo

| Upgrade | What changes |
|---------|--------------|
| Real hotel data (RapidAPI) | Searcher teammate only — same output file schema |
| Notifier teammate (email/Slack on completion) | Add task `notify` depending on `export` |
| Multi-city parallel search | Multiple `search-{city}` tasks, one Searcher per city |
| Analyst teammate (sentiment scoring) | Add task `analyze` between `extract` and `process` |
| Competing filter strategies | Two Processor teammates with different filters, Lead compares |
| Schedule daily | Claude Code `/schedule` — runs the whole team on a cron |
