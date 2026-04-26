"""Configuration module - loads env vars and defines constants."""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = Path(os.getenv("DATA_DIR", "data/sample"))
if not DATA_DIR.is_absolute():
    DATA_DIR = BASE_DIR / DATA_DIR

# API
AEC_API_KEY = os.getenv("AEC_API_KEY", "")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
REFRESH_INTERVAL = int(os.getenv("REFRESH_INTERVAL", "30"))

# Election constants
RECOUNT_THRESHOLD = 100
RECOUNT_MODERATE_THRESHOLD = 500

# Party colours
PARTY_COLOURS = {
    "ALP": "#E53935",
    "LIB": "#1565C0",
    "LNP": "#1565C0",
    "NAT": "#1565C0",
    "GRN": "#2E7D32",
    "ONP": "#E65100",
    "TEAL": "#00838F",
    "IND": "#757575",
    "OTH": "#757575",
}

# Default preference flows (federal)
DEFAULT_PREF_FLOWS = {
    "GRN": {"ALP": 0.75, "LIB": 0.25},
    "IND": {"ALP": 0.55, "LIB": 0.45},
    "ONP": {"ALP": 0.30, "LIB": 0.70},
    "OTH": {"ALP": 0.50, "LIB": 0.50},
}
