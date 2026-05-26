def process_one(extracted, max_price=150.0, min_rating=7.5):
    """Apply filters to one extracted hotel. Returns hotel if it passes, else None."""
    if extracted["price_usd"] > max_price:
        return None
    if extracted["rating"] < min_rating:
        return None
    return extracted


if __name__ == "__main__":
    import argparse, json
    p = argparse.ArgumentParser(description="Processor agent — filters extracted hotels")
    p.add_argument("--hotels",     required=True, help="JSON array of extracted hotel dicts")
    p.add_argument("--max-price",  type=float, default=150.0, dest="max_price")
    p.add_argument("--min-rating", type=float, default=7.5,   dest="min_rating")
    args = p.parse_args()

    hotels = json.loads(args.hotels)
    passed = [h for h in hotels if process_one(h, args.max_price, args.min_rating)]
    print(json.dumps(passed))
