
import pandas as pd
import os

# Create sample displacement data
data = [
    # Kenya - Turkana / Kakuma
    ["Kenya", "KEN", "Turkana", "Kakuma", "2026-01-31", 12000, 2200, 450, 120, 6200, 5800],
    ["Kenya", "KEN", "Turkana", "Kakuma", "2026-02-28", 12500, 2250, 500, 150, 6400, 6100],
    ["Kenya", "KEN", "Turkana", "Kakuma", "2026-03-31", 13100, 2300, 650, 180, 6700, 6400],

    # Kenya - Garissa / Dadaab
    ["Kenya", "KEN", "Garissa", "Dadaab", "2026-01-31", 8500, 1800, 300, 90, 4300, 4200],
    ["Kenya", "KEN", "Garissa", "Dadaab", "2026-02-28", 8700, 1850, 350, 100, 4400, 4300],
    ["Kenya", "KEN", "Garissa", "Dadaab", "2026-03-31", 9000, 1900, 400, 120, 4600, 4400],

    # DR Congo - North Kivu / Goma
    ["DR Congo", "COD", "North Kivu", "Goma", "2026-01-31", 25000, 5000, 1200, 300, 12000, 13000],
    ["DR Congo", "COD", "North Kivu", "Goma", "2026-02-28", 26500, 5100, 1500, 350, 12800, 13700],
    ["DR Congo", "COD", "North Kivu", "Goma", "2026-03-31", 28000, 5200, 1800, 400, 13500, 14500],

    # DR Congo - Ituri / Bunia
    ["DR Congo", "COD", "Ituri", "Bunia", "2026-01-31", 15000, 3000, 700, 200, 7300, 7700],
    ["DR Congo", "COD", "Ituri", "Bunia", "2026-02-28", 15800, 3100, 800, 220, 7700, 8100],
    ["DR Congo", "COD", "Ituri", "Bunia", "2026-03-31", 16500, 3200, 900, 250, 8000, 8500],

    # South Sudan - Upper Nile / Malakal
    ["South Sudan", "SSD", "Upper Nile", "Malakal", "2026-01-31", 11000, 2500, 500, 150, 5300, 5700],
    ["South Sudan", "SSD", "Upper Nile", "Malakal", "2026-02-28", 11500, 2600, 600, 170, 5500, 6000],
    ["South Sudan", "SSD", "Upper Nile", "Malakal", "2026-03-31", 12000, 2700, 700, 200, 5800, 6200],

    # South Sudan - Jonglei / Bor
    ["South Sudan", "SSD", "Jonglei", "Bor", "2026-01-31", 9000, 2000, 400, 100, 4400, 4600],
    ["South Sudan", "SSD", "Jonglei", "Bor", "2026-02-28", 9500, 2100, 500, 120, 4600, 4900],
    ["South Sudan", "SSD", "Jonglei", "Bor", "2026-03-31", 10000, 2200, 600, 150, 4800, 5200],
]

columns = [
    "country",
    "iso3",
    "admin1",
    "admin2",
    "assessment_date",
    "idps_stock",
    "returnees_stock",
    "new_displacements_flow",
    "returns_flow",
    "male_idps",
    "female_idps"
]

df = pd.DataFrame(data, columns=columns)

# Approximate town-level coordinates for demonstration mapping
coordinates = {
    "Kakuma": (3.72, 34.86),
    "Dadaab": (0.05, 40.31),
    "Goma": (-1.68, 29.23),
    "Bunia": (1.56, 30.25),
    "Malakal": (9.53, 31.66),
    "Bor": (6.21, 31.56)
}

df["latitude"] = df["admin2"].map(
    lambda location: coordinates.get(location, (None, None))[0]
)

df["longitude"] = df["admin2"].map(
    lambda location: coordinates.get(location, (None, None))[1]
)

# Create output directory
os.makedirs("data/raw", exist_ok=True)

# Save dataset
output_file = "data/raw/sample_displacement_data.csv"
df.to_csv(output_file, index=False)

print("Sample displacement dataset generated successfully!")
print(f"Total records: {len(df)}")
print(f"Locations: {df['admin2'].nunique()}")
print(f"Output file: {output_file}")

print("\nCoordinate verification:")
print(
    df[["country", "admin2", "latitude", "longitude"]]
    .drop_duplicates()
    .to_string(index=False)
)
