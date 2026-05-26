"""
Streaming Pipeline — Hotel AI Extractor
========================================
Flow per hotel (all hotels run concurrently):

  [Searcher] yields hotel_N
       └─► [Extractor]   sequential — must run first
                └─► [Processor] ∥ [Exporter]   parallel

In --tmux mode each agent writes to its own log file so the
tmux pane tailing that file lights up in real time.
"""
import sys
import json
import time
import threading
import concurrent.futures
import argparse
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent))
from search  import search_hotels
from extract import extract_one
from process import process_one
from export  import init_excel, append_hotel

LOG_DIR = Path(__file__).parent.parent / "data" / "logs"

# ANSI color per agent — matches start_agent_pane.sh
COLORS = {
    "searcher":  "\033[1;96m",   # bright cyan
    "extractor": "\033[1;93m",   # bright yellow
    "processor": "\033[1;92m",   # bright green
    "exporter":  "\033[1;95m",   # bright magenta
    "reset":     "\033[0m",
}

# One lock per log file so processor and exporter can write simultaneously
_log_locks = {name: threading.Lock() for name in ("searcher", "extractor", "processor", "exporter")}


def agent_log(agent, message, tmux_mode=False):
    """Append one colored line to an agent's log file (tailed in its tmux pane)."""
    if not tmux_mode:
        return
    color = COLORS.get(agent, "")
    line  = f"{color}{message}{COLORS['reset']}\n"
    lock  = _log_locks.get(agent, threading.Lock())
    with lock:
        with open(LOG_DIR / f"{agent}.log", "a") as f:
            f.write(line)
            f.flush()


def run_pipeline(
    destination,
    checkin,
    checkout,
    max_price   = 150.0,
    min_rating  = 7.5,
    sort_by     = "rating",
    max_results = 20,
    tmux_mode   = False,
):
    nights     = (date.fromisoformat(checkout) - date.fromisoformat(checkin)).days
    base_dir   = Path(__file__).parent.parent
    excel_path = base_dir / f"output/hotels_{destination}_{checkin}.xlsx"

    if tmux_mode:
        LOG_DIR.mkdir(parents=True, exist_ok=True)

    init_excel(excel_path)

    excel_lock    = threading.Lock()
    counter_lock  = threading.Lock()
    results_lock  = threading.Lock()
    results       = []
    hotel_counter = [0]

    # Demo delays (tmux mode only) — makes the cascade visible across panes
    D_EXTRACT = 0.30 if tmux_mode else 0
    D_PROCESS = 0.25 if tmux_mode else 0
    D_EXPORT  = 0.25 if tmux_mode else 0

    # ── Orchestrator banner ────────────────────────────────────────────
    print(f"\n{'═'*68}")
    print(f"  ORCHESTRATOR  ·  {destination}  ·  {checkin} → {checkout}  ·  {nights}n")
    print(f"  max ${max_price}/night  ·  min ★{min_rating}  ·  sort by {sort_by}")
    if tmux_mode:
        print(f"  mode: TMUX  —  watch the 4 agent panes below")
    print(f"{'═'*68}\n")

    def run_hotel(raw_hotel):
        name = raw_hotel.get("name", "?")

        # ── EXTRACTOR ─────────────────────────────────────────────────
        agent_log("extractor", f"  ← {name}", tmux_mode)
        agent_log("extractor", f"    normalizing fields...", tmux_mode)
        if not tmux_mode:
            print(f"         [Extractor] ↳ {name}")
        if D_EXTRACT:
            time.sleep(D_EXTRACT)
        extracted = extract_one(raw_hotel, nights)
        agent_log("extractor", f"    ✓  ${extracted['price_usd']}/night  ★{extracted['rating']}  {extracted['location']}", tmux_mode)

        # ── PROCESSOR ∥ EXPORTER ──────────────────────────────────────
        if not tmux_mode:
            print(f"  [Processor ∥ Exporter] ↳ {name}")

        with counter_lock:
            hotel_counter[0] += 1
            row_num = hotel_counter[0]

        proc_result = [None]

        def do_process():
            agent_log("processor", f"  ← {name}", tmux_mode)
            agent_log("processor", f"    checking  ${extracted['price_usd']} ≤ ${max_price}  ★{extracted['rating']} ≥ ★{min_rating}", tmux_mode)
            if D_PROCESS:
                time.sleep(D_PROCESS)
            proc_result[0] = process_one(extracted, max_price, min_rating)
            if proc_result[0]:
                agent_log("processor", f"    ✓ PASS  {name}", tmux_mode)
            else:
                agent_log("processor", f"    ✗ FILTERED  {name}", tmux_mode)

        def do_export():
            agent_log("exporter", f"  ← {name}  [row {row_num}]", tmux_mode)
            agent_log("exporter", f"    writing to Excel...", tmux_mode)
            if D_EXPORT:
                time.sleep(D_EXPORT)
            append_hotel(extracted, row_num, excel_path, excel_lock)
            agent_log("exporter", f"    ✓ row {row_num} written  {name}", tmux_mode)

        t_proc = threading.Thread(target=do_process, daemon=True)
        t_exp  = threading.Thread(target=do_export,  daemon=True)
        t_proc.start()
        t_exp.start()
        t_proc.join()
        t_exp.join()

        passed = proc_result[0] is not None
        if passed:
            with results_lock:
                results.append(proc_result[0])

        if tmux_mode:
            mark = "✓" if passed else "✗ filtered"
            print(f"  {mark:<10} {name:<44} ★{extracted['rating']}  ${extracted['price_usd']}")
        else:
            mark = "✓" if passed else "✗ filtered"
            print(f"  {mark:<8} {name:<44} ${extracted['price_usd']}/night  ★{extracted['rating']}  {extracted['location']}")

        return proc_result[0]

    # ── Main loop: each yielded hotel is immediately pipelined ─────────
    def searcher_gen():
        for raw in search_hotels(destination, checkin, checkout,
                                 max_price, min_rating, max_results):
            agent_log("searcher", f"  Found →  {raw['name']}", tmux_mode)
            agent_log("searcher", f"           ${raw['price']}/night  ★{raw['rating']}  {raw['location']}", tmux_mode)
            yield raw

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        futures = [
            pool.submit(run_hotel, raw)
            for raw in searcher_gen()
        ]
        concurrent.futures.wait(futures)

    # ── Sort & finalize ────────────────────────────────────────────────
    key_map = {"rating": (lambda h: h["rating"],    True),
               "price":  (lambda h: h["price_usd"], False)}
    key_fn, reverse = key_map.get(sort_by, (lambda h: h["rating"], True))
    results.sort(key=key_fn, reverse=reverse)
    top20 = results[:20]

    # Rewrite Excel in sorted order
    init_excel(excel_path)
    for i, hotel in enumerate(top20, 1):
        append_hotel(hotel, i, excel_path, excel_lock)

    # Save processed JSON
    proc_path = base_dir / f"data/processed_{destination}_{checkin}.json"
    proc_path.parent.mkdir(parents=True, exist_ok=True)
    with open(proc_path, "w") as f:
        json.dump(top20, f, indent=2)

    # ── Final results table ────────────────────────────────────────────
    W = 98
    print(f"\n{'═'*W}")
    print(f"  RESULTS  ·  {destination}  ·  {checkin} → {checkout}  ·  {nights}n  ·  sorted by {sort_by}")
    print(f"{'═'*W}")
    print(f"  {'#':<4} {'Hotel Name':<44} {'$/night':<12} {'Total':<12} {'★':<7} Location")
    print(f"  {'─'*W}")
    for i, h in enumerate(top20, 1):
        print(f"  {i:<4} {h['hotel_name']:<44} ${h['price_usd']:<11.2f} ${h['total_price_usd']:<11.2f} {h['rating']:<7} {h['location']}")
    print(f"  {'─'*W}")
    print(f"\n  Excel  →  {excel_path}")
    print(f"  Data   →  {proc_path}\n")

    return top20


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="HotelAIExtractor streaming pipeline")
    p.add_argument("--destination", default="Singapore")
    p.add_argument("--checkin",     default="2026-06-01")
    p.add_argument("--checkout",    default="2026-06-04")
    p.add_argument("--max-price",   type=float, default=150.0,  dest="max_price")
    p.add_argument("--min-rating",  type=float, default=7.5,    dest="min_rating")
    p.add_argument("--sort-by",     default="rating",           dest="sort_by")
    p.add_argument("--max-results", type=int,   default=20,     dest="max_results")
    p.add_argument("--tmux",        action="store_true",        help="Write agent logs to data/logs/ for tmux panes")
    args = p.parse_args()

    run_pipeline(
        destination = args.destination,
        checkin     = args.checkin,
        checkout    = args.checkout,
        max_price   = args.max_price,
        min_rating  = args.min_rating,
        sort_by     = args.sort_by,
        max_results = args.max_results,
        tmux_mode   = args.tmux,
    )
