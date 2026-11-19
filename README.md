# 🌍 ReliefLens

**An Interactive Geographic Data Explorer for Humanitarian Research in Ethiopia**

ReliefLens is a Python-based data exploration project designed to organize, validate, and visualize geographic information that can support humanitarian research and planning in Ethiopia.

The current prototype focuses on Ethiopia's administrative divisions. It provides an interactive map, geographic filters, data quality checks, and a searchable table of administrative locations.

**Project status:** Working prototype. Humanitarian incident and needs data have not yet been integrated.

## Features

- **Interactive map:** Explore Ethiopian administrative locations using geographic coordinates.
- **Regional filtering:** Select a region to view its associated administrative locations and zones.
- **Administrative-level filtering:** Explore records by administrative level.
- **Data quality dashboard:** Review automated validation results for missing identifiers, duplicate IDs, invalid administrative levels, invalid coordinates, and invalid parent references.
- **Location records:** View geographic information in an interactive table.
- **Automated tests:** Run unit tests to verify data validation behavior.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Data processing and application logic |
| Pandas | Data loading, cleaning, and validation |
| Streamlit | Interactive web dashboard |
| PyDeck | Geographic visualization |
| Plotly | Data visualization |
| Pytest | Automated testing |
| Git and GitHub | Version control |

## Dataset

**Source:** [Open Admin Data: Ethiopia Administrative Divisions](https://github.com/open-admin-data/ethiopia-administrative-divisions)

The current dataset contains:

- 122 administrative location records
- 15 region-level records
- 107 zone-level records
- 19 data columns

The dataset includes administrative names, identifiers, parent-child relationships, and geographic point coordinates.

**Important:** These coordinates represent administrative reference points, not administrative boundary polygons.

The administrative data should not be interpreted as evidence of current humanitarian conditions.

## Data Validation

ReliefLens includes an automated data validation pipeline that checks for:

1. Missing identifiers
2. Duplicate identifiers
3. Invalid administrative levels
4. Invalid geographic coordinates
5. Invalid parent references

The current dataset passed all five configured validation checks, with zero flagged records.

These results do not guarantee that the dataset is geographically complete, current, or free from all errors.

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/tkorga/relieflens.git
cd relieflens
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install pandas requests pytest streamlit pydeck plotly
```

### 4. Run the dashboard

```bash
python -m streamlit run app.py
```

Streamlit will provide a local URL, usually `http://localhost:8501`.

### 5. Run automated tests

```bash
python -m pytest tests/ -v
```

### 6. Regenerate the data validation report

```bash
python -m src.inspect_data
```

## Project Structure

```text
relieflens/
├── app.py
├── data/
│   ├── raw/
│   │   └── ethiopia_admin.csv
│   └── processed/
│       └── ethiopia_admin_clean.csv
├── reports/
│   └── data_profile.json
├── src/
│   ├── __init__.py
│   ├── inspect_data.py
│   └── validation.py
├── tests/
│   └── test_validation.py
├── .gitignore
└── README.md
```

## Future Development

Planned improvements include:

- Integrating humanitarian incident and displacement datasets from credible sources
- Adding geographic and temporal filters for humanitarian events
- Visualizing humanitarian indicators with clear source attribution
- Supporting regional comparisons and downloadable summaries
- Improving geographic coverage and data documentation

Future indicators will be clearly distinguished from administrative reference data.

## Responsible Data Use

ReliefLens is an exploratory research prototype, not an operational humanitarian decision-making system.

The application does not currently measure humanitarian needs, disaster severity, population vulnerability, or aid requirements.

Data sources, geographic coverage, reporting dates, and limitations should be evaluated before using any future humanitarian indicators.

## Author

**Tigistu Korga**  
Computer Science, Whitman College

GitHub: [@tkorga](https://github.com/tkorga)

## Acknowledgments

Administrative data provided by Open Admin Data. Geographic basemap attribution is displayed within the application.