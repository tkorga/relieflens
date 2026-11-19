from src.validation import validate_records
from pathlib import Path
import json
import pandas as pd

# Project paths
ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data/raw/ethiopia_admin.csv"
REPORT_PATH = ROOT / "reports/data_profile.json"

# Load data, skipping the publisher attribution comment
df = pd.read_csv(DATA_PATH, comment="#", dtype={"id": "string", "parent.id": "string"})

print("\n=== RELIEFLENS: ETHIOPIA DATA PROFILE ===")
print(f"Total records: {len(df)}")
print(f"Total columns: {len(df.columns)}")

print("\nColumns:")
print(df.columns.tolist())

print("\nAdministrative levels:")
print(df["level"].value_counts(dropna=False).to_string())

print("\nMissing values:")
print(df.isna().sum().to_string())

print("\nFirst five records:")
print(
    df[["id", "name.en", "level", "geo.lat", "geo.lon"]]
    .head()
    .to_string(index=False)
)

# Convert coordinates to numeric values
lat = pd.to_numeric(df["geo.lat"], errors="coerce")
lon = pd.to_numeric(df["geo.lon"], errors="coerce")

# Run the reusable, tested validation rules
flags = validate_records(df)

issues = {
    column: int(flags[column].sum())
    for column in flags.columns
}

flagged_records = int(flags.any(axis=1).sum())

report = {
    "project": "ReliefLens",
    "dataset": "Ethiopia Administrative Divisions",
    "total_records": len(df),
    "total_columns": len(df.columns),
    "flagged_records": flagged_records,
    "issues": issues,
}

REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)

with REPORT_PATH.open("w", encoding="utf-8") as file:
    json.dump(report, file, indent=2)

print("\n=== DATA QUALITY RESULTS ===")
for issue, count in issues.items():
    print(f"{issue}: {count}")

print(f"\nUnique flagged records: {flagged_records}")
print(f"Report saved to: {REPORT_PATH}")

# Export records that passed all validation checks
OUTPUT_PATH = ROOT / "data/processed/ethiopia_admin_clean.csv"

valid_mask = ~flags.any(axis=1)

clean_df = df.loc[valid_mask].copy()

OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

clean_df.to_csv(OUTPUT_PATH, index=False)

print("\n=== CLEAN DATA EXPORT ===")
print(f"Validated records: {len(clean_df)}")
print(f"Excluded records: {(~valid_mask).sum()}")
print(f"Clean dataset saved to: {OUTPUT_PATH}")
