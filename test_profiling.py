
import pandas as pd

from modules.data_profiling import profile_dataset

# Sample humanitarian displacement data
data = {
    "country": [
        "Kenya", "Kenya", "DRC", "South Sudan", "Kenya"
    ],
    "region": [
        "Turkana", "Turkana", "North Kivu",
        "Upper Nile", "Garissa"
    ],
    "idps": [
        12000, 15000, 25000, 18000, None
    ],
    "returnees": [
        2000, 2500, 3000, 1500, 1000
    ]
}

df = pd.DataFrame(data)

report = profile_dataset(df)

print("TOTAL RECORDS:", report["total_records"])
print("TOTAL COLUMNS:", report["total_columns"])
print("DUPLICATES:", report["duplicate_count"])

print("\nMISSING VALUES")
print(report["missing_report"])

print("\nNUMERIC SUMMARY")
print(report["numeric_summary"])
