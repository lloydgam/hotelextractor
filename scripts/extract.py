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
    p = argparse.ArgumentParser(description="Extractor agent — normalizes raw hotel JSON")
    p.add_argument("--hotels", required=True, help="JSON array of raw hotel dicts from Searcher")
    p.add_argument("--nights", type=int, default=3)
    args = p.parse_args()

    raw_hotels = json.loads(args.hotels)
    extracted  = [extract_one(h, args.nights) for h in raw_hotels]
    print(json.dumps(extracted))
