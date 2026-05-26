def extract_one(raw, nights=3):
    """Normalize one raw hotel dict into a clean structured record."""
    price = round(float(raw.get("price", 0)), 2)
    return {
        "hotel_name":      str(raw.get("name", "")).strip(),
        "price_usd":       price,
        "total_price_usd": round(price * nights, 2),
        "rating":          round(float(raw.get("rating", 0)), 1),
        "location":        str(raw.get("location", "")).strip(),
        "nights":          nights,
    }


if __name__ == "__main__":
    import argparse, json
    from pathlib import Path
    p = argparse.ArgumentParser(description="Extractor agent — normalizes raw hotel JSON")
    p.add_argument("--hotels", help="JSON array of raw hotel dicts (use --input for file handoff)")
    p.add_argument("--input",  help="Read raw hotels from JSON file (teammate file handoff)")
    p.add_argument("--output", help="Write extracted hotels to JSON file")
    p.add_argument("--nights", type=int, default=3)
    args = p.parse_args()

    if args.input:
        with open(args.input) as f:
            raw_hotels = json.load(f)
    else:
        raw_hotels = json.loads(args.hotels)

    extracted = [extract_one(h, args.nights) for h in raw_hotels]

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w") as f:
            json.dump(extracted, f, indent=2)
    else:
        print(json.dumps(extracted))
