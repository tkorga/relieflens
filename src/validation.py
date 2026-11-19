
import pandas as pd


def validate_records(df):
    """Return a Boolean DataFrame of data-quality issues."""

    ids = df["id"].astype("string")
    parents = df["parent.id"].astype("string")

    levels = pd.to_numeric(df["level"], errors="coerce")
    lat = pd.to_numeric(df["geo.lat"], errors="coerce")
    lon = pd.to_numeric(df["geo.lon"], errors="coerce")

    missing_ids = ids.isna() | ids.str.strip().eq("").fillna(True)

    duplicate_ids = ids.duplicated(keep=False) & ~missing_ids

    invalid_levels = ~levels.isin([1, 2])

    invalid_coordinates = (
        lat.isna()
        | lon.isna()
        | ~lat.between(-90, 90)
        | ~lon.between(-180, 180)
    )

    region_ids = set(ids.loc[levels == 1].dropna())

    invalid_parents = (
        levels.eq(2)
        & ~parents.isin(region_ids)
    )

    return pd.DataFrame({
        "missing_id": missing_ids,
        "duplicate_id": duplicate_ids,
        "invalid_level": invalid_levels,
        "invalid_coordinates": invalid_coordinates,
        "invalid_parent": invalid_parents,
    }, index=df.index).fillna(False).astype(bool)
