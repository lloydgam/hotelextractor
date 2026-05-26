def process_one(extracted, max_price=150.0, min_rating=7.5):
    """Apply filters to one extracted hotel. Returns hotel if it passes, else None."""
    if extracted["price_usd"] > max_price:
        return None
    if extracted["rating"] < min_rating:
        return None
    return extracted


if __name__ == "__main__":
    import argparse, json
    from pathlib import Path
    p = argparse.ArgumentParser(description="Processor agent — filters extracted hotels")
    p.add_argument("--hotels",     help="JSON array of extracted hotel dicts (use --input for file handoff)")
    p.add_argument("--input",      help="Read extracted hotels from JSON file (teammate file handoff)")
    p.add_argument("--output",     help="Write passing hotels to JSON file")
    p.add_argument("--max-price",  type=float, default=150.0, dest="max_price")
    p.add_argument("--min-rating", type=float, default=7.5,   dest="min_rating")
    args = p.parse_args()

    if args.input:
        with open(args.input) as f:
            hotels = json.load(f)
    else:
        hotels = json.loads(args.hotels)

    passed = [h for h in hotels if process_one(h, args.max_price, args.min_rating)]

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w") as f:
            json.dump(passed, f, indent=2)
    else:
        print(json.dumps(passed))
