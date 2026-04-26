# Data Sources

## Australian Electoral Commission (AEC)

The primary data source for federal elections is the Australian Electoral Commission.

### AEC Data Feeds

| Feed | URL | Description |
|---|---|---|
| Virtual Tally Room | https://results.aec.gov.au | Live election night results |
| Candidate CSV | https://results.aec.gov.au/.../ | Candidate details by election |
| Booth Results | https://results.aec.gov.au/.../ | Booth-level primary and TCP results |
| Declaration Votes | https://results.aec.gov.au/.../ | Postal, pre-poll, absent, provisional |
| Previous Elections | https://results.aec.gov.au | Historical data for swing calculation |

### Data Format

The AEC publishes data in the following formats:
- CSV exports from the Virtual Tally Room
- XML/JSON feeds for real-time updates (API key required)

### Updating Live Count Data

1. Download booth results CSV from the AEC Virtual Tally Room
2. Rename and format columns to match `data/schemas/live_count_schema.json`
3. Save to `data/sample/live_count.csv` (or configure `DATA_DIR` in `.env`)
4. Click **Refresh Data** in the app sidebar

## State Electoral Commissions

| State | Commission | URL |
|---|---|---|
| NSW | NSW Electoral Commission | https://elections.nsw.gov.au |
| VIC | Victorian Electoral Commission | https://www.vec.vic.gov.au |
| QLD | Electoral Commission of Queensland | https://www.ecq.qld.gov.au |
| SA | Electoral Commission SA | https://www.ecsa.sa.gov.au |
| WA | Western Australian Electoral Commission | https://www.elections.wa.gov.au |
| TAS | Tasmanian Electoral Commission | https://www.tec.tas.gov.au |

## Polling Data

Poll data can be manually entered via the **Prediction** page poll aggregator form, or pre-loaded in session state.

### Poll Data Format

```json
{
  "date": "2026-04-01",
  "pollster": "YouGov",
  "alp": 38.0,
  "lib": 35.0,
  "grn": 14.0,
  "ind": 10.0,
  "others": 3.0
}
```

## Geographic Data

Booth coordinates are sourced from the AEC's polling place data, available at:
https://www.aec.gov.au/Elections/Federal_Elections/

Electorate boundary GeoJSON files can be uploaded directly in the **Map** page.

## Historical Elections

Historical booth results for previous elections are available from the AEC in CSV format. These are used for swing calculation. Format your historical data to match `data/sample/historical_booths.csv`.
