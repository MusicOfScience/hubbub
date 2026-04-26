"""Utility helper functions."""
import json
from pathlib import Path
from typing import Union

from backend.config import PARTY_COLOURS, DATA_DIR


def format_votes(n: int) -> str:
    """Format vote count with commas: 12345 -> '12,345'."""
    return f"{int(n):,}"


def format_margin(n: int) -> str:
    """Format margin with sign and commas: 1234 -> '+1,234'."""
    if n >= 0:
        return f"+{int(n):,}"
    return f"{int(n):,}"


def format_pct(f: float, dp: int = 1) -> str:
    """Format percentage: 38.234 -> '38.2%'."""
    return f"{f:.{dp}f}%"


def party_colour(party_abbrev: str) -> str:
    """Return hex colour for party abbreviation."""
    return PARTY_COLOURS.get(party_abbrev.upper(), "#757575")


def swing_arrow(swing: float) -> str:
    """Return formatted swing string with arrow: 2.3 -> '↑ 2.3%'."""
    if swing >= 0:
        return f"↑ {abs(swing):.1f}%"
    return f"↓ {abs(swing):.1f}%"


def get_data_dir() -> Path:
    """Return the configured data directory."""
    return DATA_DIR


def load_json(path: Union[str, Path]) -> dict:
    """Load JSON from file path."""
    with open(path, "r") as f:
        return json.load(f)


def save_json(data: dict, path: Union[str, Path]):
    """Save dict as JSON to file path."""
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
