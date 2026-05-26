"""
Streaming Pipeline — Hotel AI Extractor
========================================
Flow per hotel (all hotels run concurrently):

  [Searcher] yields hotel_N
       └─► [Extractor]  (sequential — must run first)
                └─► [Processor] ∥ [Exporter]  (parallel)

All hotels flow through the pipeline simultaneously.
Final sort + Excel rewrite happens once all are done.
"""
import sys
import json
import threading
import concurrent.futures
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent))
from search  import search_hotels
from extract import extract_one
from process import process_one
from export  import init_excel, append_hotel


def run_pipeline(
    destination,
    checkin,
    checkout,
    max_price   = 150.0,
    min_rating  = 7.5,
    sort_by     = "rating",
    max_results = 20,
):
    nights     = (date.fromisoformat(checkout) - date.fromisoformat(checkin)).days
    base_dir   = Path(__file__).parent.parent
    excel_path = base_dir / f"output/hotels_{destination}_{checkin}.xlsx"

    init_excel(excel_path)

    excel_lock    = threading.Lock()
    counter_lock  = threading.Lock()
    results_lock  = threading.Lock()
    results       = []
    hotel_counter = [0]

    print(f"\n{'═'*68}")
    print(f"  PIPELINE  ·  {destination}  ·  {checkin} → {checkout}  ·  {nights} nights")
    print(f"  max ${max_price}/night  ·  min ★{min_rating}  ·  sort by {sort_by}")
    print(f"{'═'*68}\n")

    def run_hotel(raw_hotel):
        name = raw_hotel.get("name", "?")

        # ── Step 1: Extractor (must finish before process/export) ─────
        print(f"         [Extractor] ↳ {name}")
        extracted = extract_one(raw_hotel, nights)

        # ── Step 2: Processor ∥ Exporter ─────────────────────────────
        print(f"  [Processor ∥ Exporter] ↳ {name}")

        with counter_lock:
            hotel_counter[0] += 1
            row_num = hotel_counter[0]

        proc_result = [None]

        def do_process():
            proc_result[0] = process_one(extracted, max_price, min_rating)

        def do_export():
            append_hotel(extracted, row_num, excel_path, excel_lock)

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

        mark = "✓" if passed else "✗ filtered"
        print(f"  {mark:<8} {name:<44} ${extracted['price_usd']}/night  ★{extracted['rating']}  {extracted['location']}")

        return proc_result[0]

    # ── Main loop: search yields one hotel → immediately pipeline it ──
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        futures = [
            pool.submit(run_hotel, raw)
            for raw in search_hotels(destination, checkin, checkout,
                                     max_price, min_rating, max_results)
        ]
        concurrent.futures.wait(futures)

    # ── Sort results ──────────────────────────────────────────────────
    key_map = {"rating": (lambda h: h["rating"],     True),
               "price":  (lambda h: h["price_usd"],  False)}
    key_fn, reverse = key_map.get(sort_by, (lambda h: h["rating"], True))
    results.sort(key=key_fn, reverse=reverse)
    top20 = results[:20]

    # Rewrite Excel in final sorted order
    init_excel(excel_path)
    for i, hotel in enumerate(top20, 1):
        append_hotel(hotel, i, excel_path, excel_lock)

    # Save processed JSON
    proc_path = base_dir / f"data/processed_{destination}_{checkin}.json"
    proc_path.parent.mkdir(parents=True, exist_ok=True)
    with open(proc_path, "w") as f:
        json.dump(top20, f, indent=2)

    # ── Final table ───────────────────────────────────────────────────
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
    run_pipeline(
        destination = "Bangkok",
        checkin     = "2026-06-01",
        checkout    = "2026-06-04",
        max_price   = 150.0,
        min_rating  = 7.5,
        sort_by     = "rating",
        max_results = 20,
    )
