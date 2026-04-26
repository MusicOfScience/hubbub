# Adding a New Election

This guide walks through configuring MOE for a new election.

## Step 1: Create Data Directory

```bash
mkdir -p data/my_election_2026
```

## Step 2: Create Election Config

Copy and edit the template:
```bash
cp data/sample/election_config.json data/my_election_2026/election_config.json
```

Edit `election_config.json`:
```json
{
  "election_id": "my_electorate_2026",
  "electorate": "My Electorate",
  "state": "Victoria",
  "level": "federal",
  "election_date": "2026-05-17",
  "enrolled_voters": 95000,
  "previous_election_date": "2022-05-21",
  "tcp_candidates": ["candidate_a_id", "candidate_b_id"],
  "candidates": [
    {
      "candidate_id": "candidate_a_id",
      "name": "Candidate A Name",
      "party": "Australian Labor Party",
      "party_abbrev": "ALP",
      "colour": "#E53935"
    },
    ...
  ],
  "vote_type_estimates": {
    "ordinary_booth": 50000,
    "pre_poll": 25000,
    "postal": 10000,
    "absent": 5000,
    "provisional": 1000
  }
}
```

### Candidate ID Convention

Use `lastname_firstname` in lowercase, e.g. `chen_sarah`, `morrison_james`.

## Step 3: Prepare Candidates CSV

```bash
cp data/sample/candidates.csv data/my_election_2026/candidates.csv
```

Update with actual candidate details. Ensure `candidate_id` values match `election_config.json`.

## Step 4: Prepare Booths CSV

Download polling place data from the AEC:
https://www.aec.gov.au/Elections/Federal_Elections/

Format as:
```csv
booth_id,booth_name,lat,lon,enrolled,division
```

The `booth_id` must match the IDs used in `live_count.csv` and `historical_booths.csv`.

## Step 5: Historical Data

Download 2022 (or most recent) booth results from the AEC and format as:
```csv
booth_id,alp_primary_pct,lib_primary_pct,grn_primary_pct,ind_primary_pct,informal_pct,alp_tcp_pct,lib_tcp_pct
```

Only include parties relevant to your election. Column names must match what the swing analysis expects.

## Step 6: Configure Environment

Edit `.env`:
```
DATA_DIR=data/my_election_2026
```

## Step 7: Validate

Run the validation check:
```python
from backend.ingestion.aec_loader import load_election_config, validate_config
import json

with open("data/my_election_2026/election_config.json") as f:
    config_dict = json.load(f)

print("Valid:", validate_config(config_dict))
election = load_election_config("data/my_election_2026/election_config.json")
print("Election:", election.electorate, election.election_date)
```

## Step 8: Customise Preferences

If the election has non-standard preference flows (e.g. a prominent teal independent), adjust defaults in:
- `backend/config.py` (`DEFAULT_PREF_FLOWS`)
- Or interactively via the Preference Model page

## Checklist

- [ ] `election_config.json` created and validated
- [ ] `candidates.csv` matches election config
- [ ] `booths.csv` with coordinates
- [ ] `historical_booths.csv` from previous election
- [ ] `declaration_votes.csv` template prepared
- [ ] `scenario_default.json` adjusted for electorate
- [ ] `DATA_DIR` set in `.env`
- [ ] App loads without errors
