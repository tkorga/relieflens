
import pandas as pd

from src.validation import validate_records


def sample_data():
    return pd.DataFrame([
        {
            "id": "ET01",
            "level": 1,
            "parent.id": None,
            "geo.lat": 13.867,
            "geo.lon": 38.904,
        },
        {
            "id": "ET0101",
            "level": 2,
            "parent.id": "ET01",
            "geo.lat": 14.235,
            "geo.lon": 38.016,
        },
    ])


def test_valid_records():
    flags = validate_records(sample_data())
    assert not flags.to_numpy().any()


def test_missing_id():
    df = sample_data()
    df.loc[1, "id"] = None

    flags = validate_records(df)
    assert flags.loc[1, "missing_id"]


def test_duplicate_id():
    df = sample_data()
    df.loc[1, "id"] = "ET01"

    flags = validate_records(df)
    assert flags["duplicate_id"].sum() == 2


def test_invalid_level():
    df = sample_data()
    df.loc[1, "level"] = 99

    flags = validate_records(df)
    assert flags.loc[1, "invalid_level"]


def test_invalid_coordinates():
    df = sample_data()
    df.loc[1, "geo.lat"] = 150

    flags = validate_records(df)
    assert flags.loc[1, "invalid_coordinates"]


def test_invalid_parent():
    df = sample_data()
    df.loc[1, "parent.id"] = "UNKNOWN"

    flags = validate_records(df)
    assert flags.loc[1, "invalid_parent"]
