"""Swing analysis functions."""
from typing import Dict, List

import pandas as pd


def calculate_primary_swing(current: float, previous: float) -> float:
    """Calculate primary vote swing (percentage points)."""
    return round(current - previous, 2)


def calculate_tcp_swing(current_tcp: float, previous_tcp: float) -> float:
    """Calculate TCP swing (percentage points)."""
    return round(current_tcp - previous_tcp, 2)


def booth_level_swings(
    booths_current: pd.DataFrame, booths_historical: pd.DataFrame
) -> pd.DataFrame:
    """
    Calculate booth-level swings between current and historical results.
    Both DataFrames must have booth_id as a column.
    """
    if booths_current.empty or booths_historical.empty:
        return pd.DataFrame()

    merged = booths_current.merge(booths_historical, on="booth_id", suffixes=("_curr", "_hist"))

    result = merged[["booth_id"]].copy()

    for party in ["alp", "lib", "grn", "ind"]:
        curr_col = f"{party}_primary_pct_curr"
        hist_col = f"{party}_primary_pct_hist"
        if curr_col in merged.columns and hist_col in merged.columns:
            result[f"{party}_swing"] = (merged[curr_col] - merged[hist_col]).round(2)

    tcp_curr = "alp_tcp_pct_curr"
    tcp_hist = "alp_tcp_pct_hist"
    if tcp_curr in merged.columns and tcp_hist in merged.columns:
        result["alp_tcp_swing"] = (merged[tcp_curr] - merged[tcp_hist]).round(2)

    return result


def apply_swing_scenario(base_votes: Dict[str, float], swing_adjustments: Dict[str, float]) -> Dict[str, float]:
    """
    Apply swing adjustments to base vote shares.
    base_votes: {"ALP": 38.0, "LIB": 35.0, ...}
    swing_adjustments: {"ALP": 2.0, "LIB": -1.0, ...}
    Returns adjusted vote dict, normalised so shares sum to the original total.
    """
    adjusted = {}
    for party, share in base_votes.items():
        adjusted[party] = share + swing_adjustments.get(party, 0.0)

    # Clamp to 0
    adjusted = {k: max(0.0, v) for k, v in adjusted.items()}
    total = sum(adjusted.values())
    if total > 0:
        original_total = sum(base_votes.values())
        scale = original_total / total
        adjusted = {k: round(v * scale, 2) for k, v in adjusted.items()}

    return adjusted


def weighted_swing(swings: List[float], weights: List[float]) -> float:
    """Calculate enrollment-weighted average swing."""
    if not swings or not weights or len(swings) != len(weights):
        return 0.0
    total_weight = sum(weights)
    if total_weight == 0:
        return 0.0
    return round(sum(s * w for s, w in zip(swings, weights)) / total_weight, 2)
