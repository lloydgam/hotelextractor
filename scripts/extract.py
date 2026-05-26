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
