import pandas as pd
from datetime import date

# Boracay Hotels — Apr 2-4, 2026 | Max ₱5,000 | Min Rating 4.0 | Hotels only
# Prices in PHP per night, sorted by Price → Rating → Location
hotels = [
    {"Hotel Name": "The Beach Anne Boracay", "Price (PHP)": 780, "Rating": 8.0, "Location": "Station 1"},
    {"Hotel Name": "Hostel Avenue Boracay", "Price (PHP)": 900, "Rating": 7.5, "Location": "Manoc-Manoc"},
    {"Hotel Name": "RedDoorz @ Recson Boracay", "Price (PHP)": 1100, "Rating": 7.2, "Location": "Balabag"},
    {"Hotel Name": "OYO 876 Escurel Inn Boracay", "Price (PHP)": 1200, "Rating": 7.0, "Location": "Balabag"},
    {"Hotel Name": "AJ Travellers Inn Annex", "Price (PHP)": 1350, "Rating": 7.3, "Location": "Station 2"},
    {"Hotel Name": "M&E Guesthouse Boracay", "Price (PHP)": 1400, "Rating": 7.5, "Location": "Manoc-Manoc"},
    {"Hotel Name": "Stay Inn Station 2 by RedDoorz", "Price (PHP)": 1500, "Rating": 7.4, "Location": "Station 2"},
    {"Hotel Name": "Jejsellends Garden Cottages", "Price (PHP)": 1600, "Rating": 7.1, "Location": "Manoc-Manoc"},
    {"Hotel Name": "Shore Time Hotel Annex", "Price (PHP)": 1800, "Rating": 7.8, "Location": "Station 2"},
    {"Hotel Name": "La Bella Casa de Boracay", "Price (PHP)": 1900, "Rating": 7.6, "Location": "Station 3"},
    {"Hotel Name": "Turtle Inn Resort Boracay", "Price (PHP)": 2000, "Rating": 8.2, "Location": "Station 3"},
    {"Hotel Name": "La Carmela de Boracay", "Price (PHP)": 2070, "Rating": 8.0, "Location": "Station 2"},
    {"Hotel Name": "Boracay Midtown Hotel", "Price (PHP)": 2200, "Rating": 7.8, "Location": "Station 2"},
    {"Hotel Name": "Secret Garden Resort Boracay", "Price (PHP)": 2400, "Rating": 8.1, "Location": "Station 3"},
    {"Hotel Name": "Boracay Morning Beach Resort", "Price (PHP)": 2500, "Rating": 8.0, "Location": "Station 1"},
    {"Hotel Name": "The Tides Hotel Boracay", "Price (PHP)": 2600, "Rating": 8.3, "Location": "Station 2"},
    {"Hotel Name": "Commander Suites de Boracay", "Price (PHP)": 2800, "Rating": 7.9, "Location": "Balabag"},
    {"Hotel Name": "Diamond Water Edge Resort", "Price (PHP)": 3000, "Rating": 8.3, "Location": "Station 1"},
    {"Hotel Name": "Surfside Boracay Resort", "Price (PHP)": 3200, "Rating": 9.0, "Location": "Station 3"},
    {"Hotel Name": "Ferra Hotel and Garden Suites", "Price (PHP)": 3300, "Rating": 8.5, "Location": "Station 2"},
    {"Hotel Name": "Boracay Actopia Resort", "Price (PHP)": 3500, "Rating": 8.3, "Location": "Manoc-Manoc"},
    {"Hotel Name": "Alta Vista de Boracay", "Price (PHP)": 3800, "Rating": 8.7, "Location": "Balabag"},
    {"Hotel Name": "Chateau de Boracay", "Price (PHP)": 4000, "Rating": 8.4, "Location": "Station 3"},
    {"Hotel Name": "IL Mare Sakura Resort Boracay", "Price (PHP)": 4200, "Rating": 9.2, "Location": "Station 1"},
    {"Hotel Name": "Henann Lagoon Resort", "Price (PHP)": 4500, "Rating": 8.8, "Location": "Station 2"},
    {"Hotel Name": "Island Inn Boracay", "Price (PHP)": 4800, "Rating": 8.6, "Location": "Station 1"},
]

df = pd.DataFrame(hotels)

# Filter: Price <= 5000 PHP, Rating >= 4.0 (all already qualify)
df = df[(df["Price (PHP)"] <= 5000) & (df["Rating"] >= 4.0)]

# Sort: Price asc, Rating desc, Location asc
df = df.sort_values(by=["Price (PHP)", "Rating", "Location"], ascending=[True, False, True])

# Top 20
df = df.head(20).reset_index(drop=True)
df.index = df.index + 1
df.index.name = "#"

# Export to Excel
output_path = "/Users/lloydgam/Documents/workgroup/demo/HotelAIExtractor/output/hotels_boracay_2026-02-17.xlsx"
df.to_excel(output_path, sheet_name="Boracay Hotels")

# Print table
print(df.to_string())
print(f"\nExported to: {output_path}")
