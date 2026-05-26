import time

HOTELS = {
    "bangkok": [
        {"name": "Capella Bangkok",                   "price": 147.0, "rating": 9.5, "location": "Riverside"},
        {"name": "Mandarin Oriental Bangkok",         "price": 135.0, "rating": 9.4, "location": "Riverside"},
        {"name": "Siam Kempinski Hotel Bangkok",      "price": 149.0, "rating": 9.3, "location": "Siam"},
        {"name": "The Peninsula Bangkok",             "price": 142.0, "rating": 9.2, "location": "Riverside"},
        {"name": "Shangri-La Bangkok",                "price": 148.0, "rating": 9.1, "location": "Riverside"},
        {"name": "Four Seasons Bangkok",              "price": 144.0, "rating": 9.1, "location": "Chao Phraya"},
        {"name": "Anantara Riverside Bangkok Resort", "price": 143.0, "rating": 9.0, "location": "Riverside"},
        {"name": "Arun Residence",                    "price": 55.0,  "rating": 9.0, "location": "Old City"},
        {"name": "Centara Grand at CentralWorld",     "price": 140.0, "rating": 8.9, "location": "Siam"},
        {"name": "VIE Hotel Bangkok MGallery",        "price": 125.0, "rating": 8.9, "location": "Siam"},
        {"name": "SO/ Bangkok",                       "price": 125.0, "rating": 8.8, "location": "Silom"},
        {"name": "The Westin Grande Sukhumvit",       "price": 145.0, "rating": 8.8, "location": "Sukhumvit"},
        {"name": "Sala Rattanakosin Hotel",           "price": 110.0, "rating": 8.8, "location": "Old City"},
        {"name": "Sindhorn Midtown Hotel Bangkok",    "price": 120.0, "rating": 8.7, "location": "Langsuan"},
        {"name": "Pullman Bangkok Hotel G",           "price": 130.0, "rating": 8.7, "location": "Silom"},
        {"name": "Riva Surya Bangkok",                "price": 99.0,  "rating": 8.7, "location": "Riverside"},
        {"name": "The Sukhumvit Hotel Bangkok",       "price": 98.0,  "rating": 8.6, "location": "Sukhumvit"},
        {"name": "Amari Bangkok",                     "price": 118.0, "rating": 8.6, "location": "Siam"},
        {"name": "Novotel Bangkok on Siam Square",    "price": 108.0, "rating": 8.5, "location": "Siam"},
        {"name": "Novotel Bangkok Sukhumvit 20",      "price": 112.0, "rating": 8.4, "location": "Sukhumvit"},
        {"name": "Citadines Sukhumvit 8 Bangkok",     "price": 87.0,  "rating": 8.3, "location": "Sukhumvit"},
        {"name": "Holiday Inn Bangkok Silom",         "price": 95.0,  "rating": 8.2, "location": "Silom"},
        {"name": "ibis Bangkok Sukhumvit 24",         "price": 58.0,  "rating": 8.1, "location": "Sukhumvit"},
        {"name": "Mercure Bangkok Siam",              "price": 82.0,  "rating": 8.0, "location": "Siam"},
        {"name": "Narai Hotel Bangkok",               "price": 72.0,  "rating": 7.9, "location": "Silom"},
        {"name": "Tawana Bangkok Hotel",              "price": 65.0,  "rating": 7.7, "location": "Silom"},
    ],
    "singapore": [
        # Over budget — will be filtered by Processor (demonstrates filter in action)
        {"name": "Raffles Hotel Singapore",           "price": 350.0, "rating": 9.6, "location": "City Hall"},
        {"name": "Capella Singapore",                 "price": 290.0, "rating": 9.4, "location": "Sentosa"},
        {"name": "The St. Regis Singapore",           "price": 220.0, "rating": 9.3, "location": "Orchard"},
        {"name": "Marina Bay Sands",                  "price": 280.0, "rating": 9.2, "location": "Marina Bay"},
        # Within budget
        {"name": "The Fullerton Hotel Singapore",     "price": 148.0, "rating": 9.1, "location": "Marina Bay"},
        {"name": "Shangri-La Singapore",              "price": 150.0, "rating": 9.0, "location": "Orchard"},
        {"name": "PARKROYAL COLLECTION Marina Bay",   "price": 149.0, "rating": 8.9, "location": "Marina Bay"},
        {"name": "Andaz Singapore",                   "price": 145.0, "rating": 8.9, "location": "Bugis"},
        {"name": "Fairmont Singapore",                "price": 148.0, "rating": 8.8, "location": "City Hall"},
        {"name": "COMO Metropolitan Singapore",       "price": 140.0, "rating": 8.8, "location": "Orchard"},
        {"name": "Pan Pacific Singapore",             "price": 148.0, "rating": 8.8, "location": "Marina Bay"},
        {"name": "Pullman Singapore Hill Street",     "price": 142.0, "rating": 8.7, "location": "Clarke Quay"},
        {"name": "Grand Hyatt Singapore",             "price": 145.0, "rating": 8.7, "location": "Orchard"},
        {"name": "Swissôtel The Stamford",            "price": 135.0, "rating": 8.6, "location": "City Hall"},
        {"name": "Hilton Singapore Orchard",          "price": 138.0, "rating": 8.5, "location": "Orchard"},
        {"name": "Mandarin Orchard Singapore",        "price": 145.0, "rating": 8.5, "location": "Orchard"},
        {"name": "Novotel Singapore on Stevens",      "price": 108.0, "rating": 8.3, "location": "Orchard"},
        {"name": "Village Hotel Bugis",               "price": 95.0,  "rating": 8.2, "location": "Bugis"},
        {"name": "Hotel Jen Orchardgateway",          "price": 98.0,  "rating": 8.1, "location": "Orchard"},
        {"name": "Amara Singapore",                   "price": 92.0,  "rating": 8.1, "location": "Tanjong Pagar"},
        {"name": "Hotel G Singapore",                 "price": 88.0,  "rating": 8.0, "location": "Bugis"},
        {"name": "M Social Singapore",                "price": 85.0,  "rating": 8.0, "location": "Robertson Quay"},
        {"name": "Holiday Inn Express Orchard Road",  "price": 78.0,  "rating": 7.8, "location": "Orchard"},
        {"name": "ibis Singapore on Bencoolen",       "price": 65.0,  "rating": 7.8, "location": "Bugis"},
        {"name": "Studio M Hotel",                    "price": 72.0,  "rating": 7.7, "location": "Robertson Quay"},
        {"name": "Fragrance Hotel Ruby",              "price": 55.0,  "rating": 7.5, "location": "Bugis"},
    ],
}


def search_hotels(destination, checkin, checkout, max_price=150.0, min_rating=7.5,
                  max_results=20, delay=0.4, silent=False):
    """Generator: yields one raw hotel at a time, simulating live discovery."""
    key   = destination.lower()
    hotels = HOTELS.get(key, HOTELS["bangkok"])

    if not silent:
        print(f"\n[Searcher]  {destination}  {checkin} → {checkout}"
              f"  |  max ${max_price}/night  min ★{min_rating}\n")

    found = 0
    for hotel in hotels:
        time.sleep(delay)
        if not silent:
            print(f"[Searcher]  Found →  {hotel['name']:<44} ${hotel['price']}/night  ★{hotel['rating']}")
        yield hotel
        found += 1
        if found >= max_results:
            if not silent:
                print(f"\n[Searcher]  Reached {found} hotels — stopping.\n")
            break


if __name__ == "__main__":
    import argparse, json
    p = argparse.ArgumentParser(description="Searcher agent — outputs raw hotel JSON")
    p.add_argument("--destination", default="Bangkok")
    p.add_argument("--checkin",     default="2026-06-01")
    p.add_argument("--checkout",    default="2026-06-04")
    p.add_argument("--max-price",   type=float, default=150.0, dest="max_price")
    p.add_argument("--min-rating",  type=float, default=7.5,   dest="min_rating")
    p.add_argument("--max-results", type=int,   default=20,    dest="max_results")
    p.add_argument("--agent",       action="store_true", help="Silent JSON mode for subagent use")
    args = p.parse_args()

    hotels = list(search_hotels(
        args.destination, args.checkin, args.checkout,
        args.max_price, args.min_rating, args.max_results,
        delay=0 if args.agent else 0.4,
        silent=args.agent,
    ))
    print(json.dumps(hotels))
