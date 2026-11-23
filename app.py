
from pathlib import Path
import json

import pandas as pd
import pydeck as pdk
import streamlit as st

st.set_page_config(
    page_title="ReliefLens | Ethiopia",
    page_icon="🌍",
    layout="wide",
)

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data/processed/ethiopia_admin_clean.csv"


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    df["geo.lat"] = pd.to_numeric(df["geo.lat"], errors="coerce")
    df["geo.lon"] = pd.to_numeric(df["geo.lon"], errors="coerce")
    return df


df = load_data()

st.title("🌍 ReliefLens")
st.caption("Ethiopia | Humanitarian Geographic Data Explorer")

st.caption(
    "Displacement data source: International Organization for Migration (IOM). "
    "Accessed on November 19, 2026. DTM API. Displacement Tracking Matrix."
)

st.markdown(
    "[IOM DTM API Data Source](https://dtm.iom.int/data-and-analysis/dtm-api)"
)

geography_tab, displacement_tab = st.tabs(
    ["🌍 Geographic Explorer", "📊 Displacement Analysis"]
)

with geography_tab:  
    with geography_tab:
        st.caption(
        "Map markers represent administrative reference locations, "
        "not individual displacement sites or incident locations."
    )

    # Sidebar filters
    # Sidebar filters
    st.sidebar.header("Explore Ethiopia")

    level_options = {
        "All locations": None,
        "Regions": 1,
        "Zones": 2,
    }

    selected_level = st.sidebar.selectbox(
        "Administrative level",
        list(level_options.keys()),
    )

    # Build a list of regions from the dataset
    regions_df = df[df["level"] == 1].copy()

    region_names = sorted(
        regions_df["name.en"].dropna().unique().tolist()
    )

    selected_region = st.sidebar.selectbox(
        "Select region",
        ["All regions"] + region_names,
    )

    # Apply administrative level filter
    filtered_df = df.copy()
    level_value = level_options[selected_level]

    if level_value is not None:
        filtered_df = filtered_df[
            filtered_df["level"] == level_value
        ]

    # Apply geographic region filter
    if selected_region != "All regions":
        selected_region_id = regions_df.loc[
            regions_df["name.en"] == selected_region, "id"
        ].iloc[0]

        filtered_df = filtered_df[
            (filtered_df["id"] == selected_region_id)
            | (filtered_df["parent.id"] == selected_region_id)
        ]

    st.sidebar.caption(
        f"Showing {len(filtered_df)} administrative locations"
    )

    # Overview metrics
    col1, col2, col3 = st.columns(3)

    col1.metric("Total locations", len(filtered_df))
    col2.metric("Regions in dataset", int((df["level"] == 1).sum()))
    col3.metric("Zones in dataset", int((df["level"] == 2).sum()))

    st.subheader("Administrative Location Map")

    map_df = filtered_df.dropna(
        subset=["geo.lat", "geo.lon"]
    ).copy()

    map_df["latitude"] = map_df["geo.lat"]
    map_df["longitude"] = map_df["geo.lon"]
    map_df["location_name"] = map_df["name.en"].fillna("Unknown")
    map_df["admin_level"] = map_df["level"].map({
        1: "Region",
        2: "Zone",
    })

    map_df["color"] = map_df["level"].apply(
        lambda level: [28, 110, 164, 190]
        if level == 1 else [237, 140, 53, 170]
    )

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=map_df,
        get_position="[longitude, latitude]",
        get_fill_color="color",
        get_radius=16000,
        radius_min_pixels=4,
        radius_max_pixels=14,
        pickable=True,
    )

    view_state = pdk.ViewState(
        latitude=9.1,
        longitude=40.5,
        zoom=5,
        pitch=0,
    )

    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip={
            "html": "<b>{location_name}</b><br/>{admin_level}",
            "style": {"color": "white"},
        },
    )

    st.pydeck_chart(deck, use_container_width=True)

    st.subheader("Location Records")

    st.dataframe(
        filtered_df[
            ["id", "name.en", "level", "parent.name.en", "geo.lat", "geo.lon"]
        ],
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "Source: Open Admin Data, Ethiopia Administrative Divisions. "
        "Administrative point coordinates are not boundary polygons."
    )


    # Data quality dashboard
    st.divider()
    st.header("Data Quality Overview")

    st.caption(
        "Quality metrics describe the full administrative dataset, "
        "regardless of the selected map filters."
    )

    required_columns = [
        "id",
        "name.en",
        "level",
        "geo.lat",
        "geo.lon",
    ]

    total_required_cells = len(df) * len(required_columns)
    missing_required_cells = int(df[required_columns].isna().sum().sum())

    completeness = (
        100 * (1 - missing_required_cells / total_required_cells)
        if total_required_cells else 0
    )

    duplicate_ids = int(df["id"].duplicated().sum())

    q1, q2, q3 = st.columns(3)

    q1.metric("Required-field completeness", f"{completeness:.1f}%")
    q2.metric("Missing required values", missing_required_cells)
    q3.metric("Duplicate IDs", duplicate_ids)

    missing_counts = df.isna().sum().sort_values(ascending=False)
    missing_counts = missing_counts[missing_counts > 0]

    st.subheader("Missing Values by Column")

    if missing_counts.empty:
        st.success("No missing values found.")
    else:
        st.bar_chart(missing_counts)

    st.info(
        "Some missing values are expected. For example, top-level regions "
        "have no parent region. Missing optional metadata does not "
        "necessarily indicate a data-quality failure."
    )

    # Automated validation report
    st.divider()
    st.header("Automated Validation Results")

    REPORT_PATH = ROOT / "reports/data_profile.json"

    @st.cache_data
    def load_validation_report():
        with open(REPORT_PATH, "r", encoding="utf-8") as file:
            return json.load(file)

    report = load_validation_report()

    r1, r2, r3 = st.columns(3)

    r1.metric("Records checked", report["total_records"])
    r2.metric("Columns checked", report["total_columns"])
    r3.metric("Flagged records", report["flagged_records"])

    st.subheader("Validation Checks")

    check_labels = {
        "missing_id": "Missing identifiers",
        "duplicate_id": "Duplicate identifiers",
        "invalid_level": "Invalid administrative levels",
        "invalid_coordinates": "Invalid coordinates",
        "invalid_parent": "Invalid parent references",
    }

    checks_df = pd.DataFrame(
        [
            {
                "Check": check_labels.get(key, key),
                "Issues found": value,
                "Result": "PASS" if value == 0 else "REVIEW",
            }
            for key, value in report["issues"].items()
        ]
    )

    st.dataframe(
        checks_df,
        width="stretch",
        hide_index=True,
    )

    if report["flagged_records"] == 0:
        st.success("All configured validation checks passed.")
    else:
        st.warning("Some records require review.")

    st.caption(
        "Validation results are generated by the ReliefLens Python "
        "data-processing pipeline. They do not independently verify "
        "the accuracy or currency of the source data."
    )

with displacement_tab:
    st.header("Historical Displacement Analysis")

    st.caption(
        "Source: IOM Displacement Tracking Matrix (DTM). "
        "Ethiopia, 2017–2024. Historical observations, not current estimates."
    )

    from src.displacement import load_data as load_displacement_data

    @st.cache_data
    def load_iom_data():
        return load_displacement_data()

    iom_df = load_iom_data()

    # Dataset overview
    c1, c2, c3 = st.columns(3)

    c1.metric("Observations", f"{len(iom_df):,}")
    c2.metric("Regions represented", iom_df["admin1Pcode"].nunique())
    c3.metric("Reporting years", iom_df["yearReportingDate"].nunique())

    st.divider()

    # Filters
    selected_operation = st.selectbox(
        "Monitoring operation",
        sorted(iom_df["operation"].unique()),
    )

    operation_df = iom_df[
        iom_df["operation"] == selected_operation
    ].copy()

    available_dates = sorted(
        operation_df["reportingDate"].unique(),
        reverse=True,
    )

    selected_date = st.selectbox(
        "Reporting date",
        available_dates,
    )

    date_df = operation_df[
        operation_df["reportingDate"] == selected_date
    ].copy()

    region_options = sorted(date_df["admin1Name"].unique())

    selected_regions = st.multiselect(
        "Destination regions",
        region_options,
        default=region_options,
    )

    filtered_iom = date_df[
        date_df["admin1Name"].isin(selected_regions)
    ].copy()

    st.caption(
        f"Showing {len(filtered_iom):,} observations "
        f"for {selected_operation} on {selected_date}."
    )

    # Chart observations by displacement reason
    st.subheader("Observations by Displacement Reason")

    if filtered_iom.empty:
        st.warning("No observations match these filters.")
    else:
        reason_counts = (
            filtered_iom["displacementReason"]
            .value_counts()
            .rename_axis("Reason")
            .reset_index(name="Observations")
            .set_index("Reason")
        )

        st.bar_chart(reason_counts)

    # Detailed records
        st.subheader("Regional Reporting Coverage")
        covered_regions = date_df["admin1Pcode"].nunique()
    total_regions = regions_df["id"].nunique()
    missing_count = total_regions - covered_regions
    coverage_pct = 100 * covered_regions / total_regions

    cov1, cov2, cov3 = st.columns(3)

    cov1.metric("Regions represented", covered_regions)
    cov2.metric("Regions missing", missing_count)
    cov3.metric("Regional coverage", f"{coverage_pct:.1f}%")

    st.caption(
        "Number of IOM observations by destination region "
        "for the selected monitoring operation and reporting date. "
        "This chart shows reporting coverage, not displacement severity."
    )

    region_counts = (
        date_df.groupby("admin1Name")
        .size()
        .sort_values(ascending=False)
        .rename("Observations")
    )

    st.bar_chart(region_counts, horizontal=True)

    st.caption(
        f"{date_df['admin1Pcode'].nunique()} of "
        f"{regions_df['id'].nunique()} administrative regions "
        "are represented in this reporting period. "
        "Unrepresented regions should not be interpreted as having zero IDPs."
    )
        # Identify regions without observations in the selected period
    missing_regions = regions_df[
        ~regions_df["id"].isin(date_df["admin1Pcode"])
    ].sort_values("name.en")

    if not missing_regions.empty:
        st.warning(
            f"{len(missing_regions)} regions have no observations "
            "in this reporting period."
        )

        st.dataframe(
            missing_regions[["id", "name.en"]].rename(
                columns={
                    "id": "Region code",
                    "name.en": "Region",
                }
            ),
            hide_index=True,
            use_container_width=True,
        )
    else:
        st.success(
            "All reference regions are represented in this reporting period."
        )
    st.subheader("Displacement Observation Records")

    display_columns = [
        "admin1Name",
        "idpOriginAdmin1Name",
        "reportingDate",
        "roundNumber",
        "displacementReason",
        "numPresentIdpInd",
        "numberMales",
        "numberFemales",
    ]

    st.dataframe(
        filtered_iom[display_columns],
        use_container_width=True,
        hide_index=True,
    )

    st.info(
        "Charts count dataset observations, not displaced people. "
        "Population figures are displayed at the individual-record level. "
        "Records from different dates or operations must not be "
        "combined into a single population estimate."
    )

    st.divider()
    st.subheader("Historical Displacement Trend")

    st.caption(
        "Explore reported IDP counts for one destination, "
        "origin, displacement reason, and monitoring operation."
    )

    trend_region = st.selectbox(
        "Trend destination region",
        sorted(iom_df["admin1Name"].unique()),
    )

    trend_region_df = iom_df[
        iom_df["admin1Name"] == trend_region
    ]

    trend_operation = st.selectbox(
        "Trend monitoring operation",
        sorted(trend_region_df["operation"].unique()),
    )

    trend_operation_df = trend_region_df[
        trend_region_df["operation"] == trend_operation
    ]

    trend_origin = st.selectbox(
        "Trend origin region",
        sorted(trend_operation_df["idpOriginAdmin1Name"].unique()),
    )

    trend_origin_df = trend_operation_df[
        trend_operation_df["idpOriginAdmin1Name"] == trend_origin
    ]

    trend_reason = st.selectbox(
        "Trend displacement reason",
        sorted(trend_origin_df["displacementReason"].unique()),
    )

    trend_df = trend_origin_df[
        trend_origin_df["displacementReason"] == trend_reason
    ].copy()

    trend_df["date"] = pd.to_datetime(trend_df["reportingDate"])

    trend_df = trend_df.sort_values("date")

    # Verify that each date contains one observation.
    from src.displacement import validate_trend_keys

    if not validate_trend_keys(trend_df):
        st.warning(
            "Multiple observations exist for some reporting dates. "
            "A single population trend cannot be displayed safely."
        )
        st.dataframe(trend_df, hide_index=True)
    else:
        chart_df = trend_df.set_index("date")[["numPresentIdpInd"]]

        st.line_chart(chart_df)

        st.caption(
            "Values represent reported IDPs for the selected "
            "origin-destination-reason combination. "
            "Dates are historical reporting periods, not live estimates."
        )