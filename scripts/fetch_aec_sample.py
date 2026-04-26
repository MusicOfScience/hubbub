"""
Demonstrates how AEC data would be fetched.
Downloads sample data from the AEC Virtual Tally Room (placeholder URL).
Writes sample CSV data locally for development/testing.
"""
import csv
import json
import os
from pathlib import Path

# NOTE: Replace with real AEC data feed URL when available
AEC_BASE_URL = "https://results.aec.gov.au"  # Placeholder

OUTPUT_DIR = Path(__file__).parent.parent / "data" / "sample"


def write_sample_live_count():
    """Write a sample live count CSV demonstrating the expected format."""
    output_path = OUTPUT_DIR / "live_count_fetched.csv"
    rows = [
        {
            "booth_id": "booth_001",
            "chen_sarah_primary": 612,
            "morrison_james_primary": 541,
            "walsh_emma_primary": 195,
            "bradley_tom_primary": 128,
            "informal": 31,
            "chen_sarah_tcp": 892,
            "morrison_james_tcp": 615,
            "total_enrolled": 4200,
            "counted_flag": 1,
        },
        {
            "booth_id": "booth_002",
            "chen_sarah_primary": 523,
            "morrison_james_primary": 489,
            "walsh_emma_primary": 178,
            "bradley_tom_primary": 112,
            "informal": 27,
            "chen_sarah_tcp": 791,
            "morrison_james_tcp": 538,
            "total_enrolled": 3800,
            "counted_flag": 1,
        },
    ]
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Sample live count written to {output_path}")


def simulate_aec_fetch():
    """
    Simulate fetching AEC data.
    In production, replace this with real HTTP requests to the AEC API.
    """
    print("=" * 60)
    print("AEC Data Fetch Simulator")
    print("=" * 60)
    print(f"AEC Base URL: {AEC_BASE_URL}")
    print("NOTE: This is a demonstration script.")
    print("      Replace AEC_BASE_URL with the real AEC feed URL.")
    print()

    # Check output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {OUTPUT_DIR}")

    # Write sample data
    write_sample_live_count()
    print()
    print("Steps to fetch real AEC data:")
    print("1. Obtain an AEC_API_KEY (contact aec.gov.au)")
    print("2. Set AEC_API_KEY in your .env file")
    print("3. Replace AEC_BASE_URL with the authenticated endpoint URL")
    print("4. Use requests.get(url, headers={'Authorization': f'Bearer {api_key}'})")
    print("5. Parse the response JSON/CSV and save to DATA_DIR/live_count.csv")
    print()
    print("Done.")


if __name__ == "__main__":
    simulate_aec_fetch()
