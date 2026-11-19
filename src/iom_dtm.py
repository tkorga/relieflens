

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv


load_dotenv()

BASE_URL = "https://dtmapi.iom.int/v3/displacement"
ROOT = Path(__file__).resolve().parents[1]
OUTPUT_FILE = ROOT / "data/raw/iom_dtm/ethiopia_admin1.json"


def api_request(endpoint, params=None):
    """Make an authenticated request to the IOM DTM API."""

    api_key = os.getenv("IOM_DTM_API_KEY")

    if not api_key:
        raise ValueError(
            "IOM_DTM_API_KEY is missing from your .env file."
        )

    headers = {
        "Ocp-Apim-Subscription-Key": api_key,
        "User-Agent": "ReliefLens-Research/1.0",
        "Accept": "application/json",
    }

    response = requests.get(
        f"{BASE_URL}/{endpoint}",
        headers=headers,
        params=params,
        timeout=60,
    )

    response.raise_for_status()

    data = response.json()

    if not isinstance(data, dict) or data.get("isSuccess") is not True:
        raise RuntimeError("IOM API returned an unsuccessful response.")

    return data


def get_countries():
    """Retrieve countries covered by the IOM DTM API."""
    return api_request("country-list")


def get_ethiopia_displacement():
    """Retrieve Ethiopia Admin 1 displacement observations."""
    return api_request(
        "admin1",
        params={"Admin0Pcode": "ETH"},
    )


def download_displacement():
    """Download and save a local Ethiopia displacement snapshot."""

    print("Downloading Ethiopia displacement data...")

    response = get_ethiopia_displacement()
    records = response.get("result")

    if not isinstance(records, list) or not records:
        raise ValueError("API returned no displacement records.")

    snapshot = {
        "source": "IOM Displacement Tracking Matrix API v3",
        "country": "Ethiopia",
        "admin_level": 1,
        "downloaded_at_utc": datetime.now(timezone.utc).isoformat(),
        "record_count": len(records),
        "records": records,
    }

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Write to a temporary file first to avoid damaging an
    # existing snapshot if the write fails.
    temporary_file = OUTPUT_FILE.with_suffix(".tmp")

    with temporary_file.open("w", encoding="utf-8") as file:
        json.dump(snapshot, file, indent=2, ensure_ascii=False)

    temporary_file.replace(OUTPUT_FILE)

    print("Download complete.")
    print("Records saved:", len(records))
    print("File:", OUTPUT_FILE)


def main():
    parser = argparse.ArgumentParser(
        description="ReliefLens IOM DTM API utilities"
    )

    parser.add_argument(
        "--download",
        action="store_true",
        help="Download the latest available Ethiopia snapshot",
    )

    parser.add_argument(
        "--countries",
        action="store_true",
        help="Retrieve the IOM country list",
    )

    args = parser.parse_args()

    if args.download:
        download_displacement()
    elif args.countries:
        response = get_countries()
        print("Countries returned:", len(response["result"]))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
