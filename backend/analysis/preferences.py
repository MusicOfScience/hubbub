"""Preference flow modelling."""
from typing import Dict, List, Tuple


class PreferenceModel:
    """Models preference flows for Australian preferential voting."""

    def __init__(self, candidates: list):
        self.candidates = candidates
        self._pref_flows: Dict[str, Dict[str, float]] = {}
        self._setup_defaults()

    def _setup_defaults(self):
        """Initialise default preference flows."""
        self._pref_flows = self.default_pref_flows()

    def default_pref_flows(self) -> Dict[str, Dict[str, float]]:
        """Standard Australian federal preference flows."""
        return {
            "GRN": {"ALP": 0.75, "LIB": 0.25},
            "IND": {"ALP": 0.55, "LIB": 0.45},
            "ONP": {"ALP": 0.30, "LIB": 0.70},
            "OTH": {"ALP": 0.50, "LIB": 0.50},
        }

    def flow_to_tcp(self, primary_votes: Dict[str, float], pref_matrix: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """
        Calculate TCP votes from primary votes and preference matrix.
        primary_votes: {"ALP": 38.0, "LIB": 35.0, "GRN": 14.0, "IND": 10.0, "informal": 3.0}
        pref_matrix: {"GRN": {"ALP": 0.75, "LIB": 0.25}, ...}
        Returns {"ALP": tcp_pct, "LIB": tcp_pct}
        """
        tcp_alp = primary_votes.get("ALP", 0.0)
        tcp_lib = primary_votes.get("LIB", 0.0)

        for party, votes in primary_votes.items():
            if party in ("ALP", "LIB", "informal"):
                continue
            flows = pref_matrix.get(party, {"ALP": 0.50, "LIB": 0.50})
            tcp_alp += votes * flows.get("ALP", 0.50)
            tcp_lib += votes * flows.get("LIB", 0.50)

        total = tcp_alp + tcp_lib
        if total > 0:
            tcp_alp = round((tcp_alp / total) * 100, 2)
            tcp_lib = round((tcp_lib / total) * 100, 2)
        return {"ALP": tcp_alp, "LIB": tcp_lib}

    def adjust_preference_flow(self, candidate_id: str, to_candidate: str, new_flow_pct: float):
        """
        Adjust preference flow for a candidate to another.
        Automatically adjusts the complementary flow to maintain 100%.
        """
        party = candidate_id.upper()
        if party not in self._pref_flows:
            self._pref_flows[party] = {"ALP": 0.50, "LIB": 0.50}

        new_flow = new_flow_pct / 100.0
        self._pref_flows[party][to_candidate] = new_flow

        # Distribute remainder to other TCP candidate
        other = "LIB" if to_candidate == "ALP" else "ALP"
        self._pref_flows[party][other] = round(1.0 - new_flow, 4)

    def calculate_exhaustion_rate(self) -> float:
        """Returns 0.0 - federal elections have compulsory preferential voting."""
        return 0.0

    def three_way_contest_resolution(self, votes: Dict[str, float]) -> Tuple[str, Tuple[str, str]]:
        """
        Determine which candidate is eliminated in a three-way contest.
        Returns (eliminated_candidate, (remaining_candidate_1, remaining_candidate_2)).
        """
        sorted_candidates = sorted(votes.items(), key=lambda x: x[1])
        eliminated = sorted_candidates[0][0]
        remaining = (sorted_candidates[1][0], sorted_candidates[2][0])
        return eliminated, remaining
