def process_one(extracted, max_price=150.0, min_rating=7.5):
    """Apply filters to one extracted hotel. Returns hotel if it passes, else None."""
    if extracted["price_usd"] > max_price:
        return None
    if extracted["rating"] < min_rating:
        return None
    return extracted
