
import argparse
import json
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data/raw/iom_dtm/ethiopia_admin1.json"

POPULATION_COLUMNS = [
    "numPresentIdpInd",
    "numberMales",
    "numberFemales",
]

OBSERVATION_KEYS = [
    "admin1Pcode",
    "reportingDate",
    "operation",
    "roundNumber",
    "displacementReason",
    "idpOriginAdmin1Pcode",
]


def load_data():
    """Load a local IOM snapshot or retrieve observations from the API."""

    if DATA_FILE.exists():
        with DATA_FILE.open("r", encoding="utf-8") as file:
            snapshot = json.load(file)
    else:
        from src.iom_dtm import get_ethiopia_displacement

        response = get_ethiopia_displacement()
        records = response.get("result")

        if not isinstance(records, list) or not records:
            raise ValueError("IOM API returned no displacement records.")

        snapshot = {
            "record_count": len(records),
            "records": records,
        }

    records = snapshot.get("records")

    if not isinstance(records, list) or not records:
        raise ValueError("Snapshot contains no valid records.")

    if snapshot.get("record_count") != len(records):
        raise ValueError("Snapshot record count does not match.")

    df = pd.DataFrame(records)

    required_columns = [
        "id",
        "admin1Name",
        "admin1Pcode",
        "reportingDate",
        "yearReportingDate",
        "roundNumber",
        "operation",
        "displacementReason",
        "idpOriginAdmin1Name",
        "idpOriginAdmin1Pcode",
        "assessmentType",
        *POPULATION_COLUMNS,
    ]

    missing = set(required_columns) - set(df.columns)

    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    return df


def validate_data(df):
    """Return integrity-check results without modifying records."""

    population = df[POPULATION_COLUMNS]

    numeric_population = population.apply(
        pd.to_numeric, errors="coerce"
    )

    invalid_population = numeric_population.isna().any(axis=1)

    negative_population = (
        numeric_population.lt(0).any(axis=1)
    )

    gender_mismatch = (
        numeric_population["numberMales"]
        + numeric_population["numberFemales"]
        != numeric_population["numPresentIdpInd"]
    )

    return {
        "missing_values": int(df.isna().sum().sum()),
        "duplicate_ids": int(df["id"].duplicated().sum()),
        "invalid_population_records": int(invalid_population.sum()),
        "negative_population_records": int(negative_population.sum()),
        "population_mismatches": int(
            (gender_mismatch & ~invalid_population).sum()
        ),
        "duplicate_observation_keys": int(
            df.duplicated(subset=OBSERVATION_KEYS, keep=False).sum()
        ),
        "exact_duplicates_excluding_id": int(
            df.drop(columns=["id"]).duplicated().sum()
        ),
    }


def profile_data(df):
    """Print dataset coverage and integrity information."""

    print("\n=== ETHIOPIA DISPLACEMENT PROFILE ===")
    print("Total records:", len(df))
    print("Total columns:", len(df.columns))

    print("\nReporting years:")
    print(df["yearReportingDate"].value_counts().sort_index().to_string())

    print("\nRegions:")
    print(sorted(df["admin1Name"].dropna().unique()))

    print("\nAssessment types:")
    print(df["assessmentType"].value_counts().to_string())

    print("\nDisplacement reasons:")
    print(df["displacementReason"].value_counts().to_string())

    print("\nOperations:")
    print(df["operation"].value_counts().to_string())

    dates = pd.to_datetime(df["reportingDate"], errors="coerce")

    print("\nEarliest reporting date:", dates.min())
    print("Latest reporting date:", dates.max())
    print("Invalid reporting dates:", int(dates.isna().sum()))

    print("\n=== VALIDATION RESULTS ===")

    for name, count in validate_data(df).items():
        print(f"{name}: {count}")


def analyze_overlaps(df):
    """Inspect repeated records and assessment-operation overlaps."""

    print("\n=== OVERLAP ANALYSIS ===")

    region_dates = df.groupby(
        ["admin1Pcode", "reportingDate"]
    ).size()

    print("Region-date combinations:", len(region_dates))
    print(
        "Region-date combinations with multiple records:",
        int((region_dates > 1).sum()),
    )

    keys_without_origin = OBSERVATION_KEYS[:-1]

    print(
        "Records sharing keys excluding origin:",
        int(
            df.duplicated(
                subset=keys_without_origin,
                keep=False,
            ).sum()
        ),
    )

    print(
        "Records sharing keys including origin:",
        int(
            df.duplicated(
                subset=OBSERVATION_KEYS,
                keep=False,
            ).sum()
        ),
    )

    operations_per_region_date = df.groupby(
        ["admin1Pcode", "reportingDate"]
    )["operation"].nunique()

    print(
        "Region-date combinations with multiple operations:",
        int((operations_per_region_date > 1).sum()),
    )

    print("\nLatest reporting date by region:")
    print(
        df.groupby("admin1Name")["reportingDate"]
        .max()
        .sort_values(ascending=False)
        .to_string()
    )

    print("\nRegions covered by each operation:")
    for operation, group in df.groupby("operation"):
        print(f"\n{operation}:")
        print(sorted(group["admin1Name"].unique()))

    print("\nRecords by operation and year:")
    print(
        pd.crosstab(
            df["yearReportingDate"],
            df["operation"],
        ).to_string()
    )

def validate_trend_keys(df):
    keys = [
        "operation",
        "admin1Pcode",
        "idpOriginAdmin1Pcode",
        "displacementReason",
        "reportingDate",
    ]

    return not df.duplicated(subset=keys).any()

def main():
    parser = argparse.ArgumentParser(
        description="ReliefLens displacement data analysis"
    )

    parser.add_argument(
        "--profile",
        action="store_true",
        help="Show dataset profile and validation results",
    )

    parser.add_argument(
        "--overlaps",
        action="store_true",
        help="Inspect overlapping observations",
    )

    args = parser.parse_args()

    df = load_data()

    if args.profile:
        profile_data(df)
    elif args.overlaps:
        analyze_overlaps(df)
    else:
        profile_data(df)
        analyze_overlaps(df)


if __name__ == "__main__":
    main()
