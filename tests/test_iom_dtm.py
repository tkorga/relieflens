
import pandas as pd
import pytest

from src.displacement import validate_data


def sample_records():
    """Create a small, valid displacement dataset."""
    return pd.DataFrame(
        [
            {
                "id": 1,
                "admin1Pcode": "ET01",
                "reportingDate": "2024-08-31",
                "operation": "Countrywide monitoring",
                "roundNumber": 1,
                "displacementReason": "Conflict",
                "idpOriginAdmin1Pcode": "ET02",
                "numPresentIdpInd": 100,
                "numberMales": 40,
                "numberFemales": 60,
            },
            {
                "id": 2,
                "admin1Pcode": "ET01",
                "reportingDate": "2024-08-31",
                "operation": "Countrywide monitoring",
                "roundNumber": 1,
                "displacementReason": "Conflict",
                "idpOriginAdmin1Pcode": "ET03",
                "numPresentIdpInd": 200,
                "numberMales": 90,
                "numberFemales": 110,
            },
        ]
    )


def test_valid_records():
    results = validate_data(sample_records())

    assert all(value == 0 for value in results.values())


def test_duplicate_ids():
    df = sample_records()
    df.loc[1, "id"] = 1

    results = validate_data(df)

    assert results["duplicate_ids"] == 1


def test_negative_population():
    df = sample_records()
    df.loc[0, "numPresentIdpInd"] = -100

    results = validate_data(df)

    assert results["negative_population_records"] == 1


def test_population_mismatch():
    df = sample_records()
    df.loc[0, "numberFemales"] = 50

    results = validate_data(df)

    assert results["population_mismatches"] == 1


def test_distinct_origins_are_not_duplicates():
    df = sample_records()

    results = validate_data(df)

    assert results["duplicate_observation_keys"] == 0


def test_duplicate_observation_keys():
    df = sample_records()
    df.loc[1, "idpOriginAdmin1Pcode"] = "ET02"

    results = validate_data(df)

    assert results["duplicate_observation_keys"] == 2


def test_missing_population():
    df = sample_records()
    df.loc[0, "numberMales"] = None

    results = validate_data(df)

    assert results["invalid_population_records"] == 1

def test_trend_keys_are_unique():
    import pandas as pd

    records = pd.DataFrame([
        {
            "operation": "Countrywide monitoring",
            "admin1Pcode": "ET04",
            "idpOriginAdmin1Pcode": "ET04",
            "displacementReason": "Conflict",
            "reportingDate": "2024-08-31",
        },
        {
            "operation": "Countrywide monitoring",
            "admin1Pcode": "ET04",
            "idpOriginAdmin1Pcode": "ET04",
            "displacementReason": "Natural disaster",
            "reportingDate": "2024-08-31",
        },
    ])

    trend_keys = [
        "operation",
        "admin1Pcode",
        "idpOriginAdmin1Pcode",
        "displacementReason",
        "reportingDate",
    ]

    from src.displacement import validate_trend_keys

    assert validate_trend_keys(records)
def test_trend_keys_reject_duplicates():
    import pandas as pd
    from src.displacement import validate_trend_keys

    records = pd.DataFrame([
        {
            "operation": "Countrywide monitoring",
            "admin1Pcode": "ET04",
            "idpOriginAdmin1Pcode": "ET04",
            "displacementReason": "Conflict",
            "reportingDate": "2024-08-31",
        },
        {
            "operation": "Countrywide monitoring",
            "admin1Pcode": "ET04",
            "idpOriginAdmin1Pcode": "ET04",
            "displacementReason": "Conflict",
            "reportingDate": "2024-08-31",
        },
    ])

    assert not validate_trend_keys(records)