"""Live count analysis functions."""
from typing import Dict, Tuple

import pandas as pd


def calculate_tcp_margin(booth_results: pd.DataFrame) -> Tuple[int, float]:
    """
    Calculate two-candidate preferred margin from booth results.
    Returns (votes_margin, pct_margin) where positive means first TCP candidate leads.
    """
    if booth_results.empty:
        return 0, 0.0

    tcp_cols = [c for c in booth_results.columns if "_tcp" in c]
    if len(tcp_cols) < 2:
        return 0, 0.0

    col_a, col_b = tcp_cols[0], tcp_cols[1]
    total_a = booth_results[col_a].sum()
    total_b = booth_results[col_b].sum()
    total = total_a + total_b

    votes_margin = int(total_a - total_b)
    pct_margin = round(((total_a / total) * 100 - 50) * 2, 2) if total > 0 else 0.0
    return votes_margin, pct_margin


def calculate_count_progress(counted: int, total: int) -> float:
    """Return percentage of votes counted (0-100)."""
    if total <= 0:
        return 0.0
    return min(100.0, round((counted / total) * 100, 2))


def estimate_outstanding_votes(
    declaration_votes: pd.DataFrame, booth_results: pd.DataFrame
) -> Dict[str, int]:
    """
    Estimate outstanding votes by type.
    Returns dict keyed by vote_type with outstanding count.
    """
    outstanding: Dict[str, int] = {}
    if declaration_votes.empty:
        return outstanding

    for _, row in declaration_votes.iterrows():
        vtype = str(row.get("vote_type", "unknown"))
        estimated = int(row.get("estimated_total", 0))
        received = int(row.get("received_count", 0))
        outstanding[vtype] = max(0, estimated - received)

    return outstanding


def project_final_margin(
    current_margin: int,
    outstanding: Dict[str, int],
    preference_assumptions: Dict[str, float],
) -> Tuple[int, Tuple[int, int]]:
    """
    Project the final margin given current margin, outstanding votes, and preference assumptions.
    preference_assumptions: {"postal": 0.46, "pre_poll": 0.52, ...} (ALP share for each type)
    Returns (projected_margin, (low, high)) confidence band.
    """
    adjustment = 0
    for vtype, count in outstanding.items():
        alp_share = preference_assumptions.get(vtype, 0.50)
        lib_share = 1.0 - alp_share
        adjustment += int(count * (alp_share - lib_share))

    projected = current_margin + adjustment
    # Simple uncertainty band: ±5% of total outstanding
    total_outstanding = sum(outstanding.values())
    uncertainty = int(total_outstanding * 0.05)
    return projected, (projected - uncertainty, projected + uncertainty)


def recount_risk(projected_margin: int) -> Tuple[str, int]:
    """
    Assess recount risk based on projected margin.
    Returns (risk_level, threshold).
    """
    margin = abs(projected_margin)
    if margin < 100:
        return "high", 100
    elif margin < 500:
        return "moderate", 500
    else:
        return "low", 500


def count_status(counted_pct: float) -> str:
    """Return count status label based on percentage counted."""
    if counted_pct < 25:
        return "early"
    elif counted_pct < 50:
        return "developing"
    elif counted_pct < 75:
        return "mature"
    else:
        return "near-final"


def required_vote_share(current_votes: Dict[str, int], outstanding_votes: Dict[str, int]) -> float:
    """
    Calculate the required percentage of outstanding votes the trailing candidate needs to win.
    current_votes: {"candidate_a": votes, "candidate_b": votes}
    outstanding_votes: dict by type, total outstanding
    Returns float (0-100) required share for the trailing candidate.
    """
    candidates = list(current_votes.keys())
    if len(candidates) < 2:
        return 50.0

    votes_a = current_votes[candidates[0]]
    votes_b = current_votes[candidates[1]]
    total_outstanding = sum(outstanding_votes.values())

    if total_outstanding <= 0:
        return 100.0 if votes_a > votes_b else 0.0

    if votes_a >= votes_b:
        # candidates[1] is trailing
        deficit = votes_a - votes_b
        required = (deficit + 1 + total_outstanding * 0.5) / total_outstanding * 100
    else:
        deficit = votes_b - votes_a
        required = (deficit + 1 + total_outstanding * 0.5) / total_outstanding * 100

    return round(min(100.0, max(0.0, required)), 1)
