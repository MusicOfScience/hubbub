# 🗳️ Margin of Error (MOE)

**Australian Election Prediction & Live-Count Analysis**

A browser-based Streamlit application for analysing Australian federal and state election results in real time, including live count tracking, two-candidate preferred (TCP) margin calculation, preference flow modelling, Monte Carlo probability simulation, and interactive swingometer.

## Features

| Page | Description |
|---|---|
| 📊 Live Count | Real-time TCP margin, count progress, recount risk, outstanding vote estimation |
| 🔮 Prediction | Monte Carlo simulation, probability of victory, poll aggregation |
| 📐 Swingometer | Interactive swing and preference scenario builder |
| 🔢 Preference Model | Preference flow matrix editor and TCP calculator |
| 🗺️ Map | Booth-level geographic visualisation with Folium |
| 🔍 Intelligence | Data upload and manual intelligence log |
| 📝 Commentary | Election night commentary timeline |
| ⬇️ Export | CSV, XLSX, HTML report downloads |

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
cd /path/to/hubbub
streamlit run frontend/app.py
# or
bash scripts/run.sh
```

The app will open at http://localhost:8501

## Project Structure

```
hubbub/
├── frontend/          # Streamlit pages and components
│   ├── app.py         # Main entry point
│   ├── pages/         # Multi-page app pages
│   ├── components/    # Reusable UI components
│   └── styles/        # Custom CSS
├── backend/           # Business logic (no Streamlit imports)
│   ├── analysis/      # Core analysis modules
│   ├── ingestion/     # Data loaders
│   ├── models/        # Data models
│   ├── export/        # Export utilities
│   └── utils/         # Helper functions
├── data/
│   ├── sample/        # Sample election data (Banksia 2026)
│   └── schemas/       # JSON schemas
├── tests/             # pytest test suite
├── docs/              # Documentation
├── scripts/           # Utility scripts
└── notebooks/         # Jupyter notebooks
```

## Configuration

Copy `.env.example` to `.env` and edit:

```bash
cp .env.example .env
```

| Variable | Default | Description |
|---|---|---|
| `AEC_API_KEY` | — | AEC API key (future use) |
| `DATA_DIR` | `data/sample` | Path to election data directory |
| `LOG_LEVEL` | `INFO` | Logging level |
| `REFRESH_INTERVAL` | `30` | Seconds between data refreshes |

## Sample Data

The repository ships with fictional sample data for **Banksia 2026** (Victoria federal electorate):

- 4 candidates: Sarah Chen (ALP), James Morrison (LIB), Emma Walsh (GRN), Tom Bradley (IND)
- 8 polling booths
- ~35,000 enrolled voters
- Partial live count (~35% counted)
- Historical 2022 results for swing calculation

## Running Tests

```bash
pytest tests/
# or with verbose output
pytest tests/ -v
```

## Documentation

- [Data Sources](docs/data_sources.md)
- [Modelling Assumptions](docs/modelling_assumptions.md)
- [Live Count Workflow](docs/live_count_workflow.md)
- [Adding a New Election](docs/adding_new_election.md)
- [Scenario Testing](docs/scenario_testing.md)

## Australian Party Colours

| Party | Colour | Hex |
|---|---|---|
| ALP | 🔴 Red | `#E53935` |
| LIB/LNP | 🔵 Blue | `#1565C0` |
| Greens | 🟢 Green | `#2E7D32` |
| One Nation | 🟠 Orange | `#E65100` |
| Teal/Independent | 🩵 Teal | `#00838F` |
| Other/IND | ⚫ Grey | `#757575` |

## Licence

MIT