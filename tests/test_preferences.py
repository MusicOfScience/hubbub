"""Tests for backend/analysis/preferences.py"""
import pytest

from backend.analysis.preferences import PreferenceModel


SAMPLE_CANDIDATES = [
    {"candidate_id": "chen_sarah", "name": "Sarah Chen", "party": "ALP", "party_abbrev": "ALP", "colour": "#E53935"},
    {"candidate_id": "morrison_james", "name": "James Morrison", "party": "LIB", "party_abbrev": "LIB", "colour": "#1565C0"},
    {"candidate_id": "walsh_emma", "name": "Emma Walsh", "party": "GRN", "party_abbrev": "GRN", "colour": "#2E7D32"},
    {"candidate_id": "bradley_tom", "name": "Tom Bradley", "party": "IND", "party_abbrev": "IND", "colour": "#757575"},
]


class TestPreferenceModel:
    def setup_method(self):
        self.model = PreferenceModel(SAMPLE_CANDIDATES)

    def test_default_pref_flows_exist(self):
        flows = self.model.default_pref_flows()
        assert "GRN" in flows
        assert "IND" in flows

    def test_grn_flows_sum_to_one(self):
        flows = self.model.default_pref_flows()
        grn_total = sum(flows["GRN"].values())
        assert abs(grn_total - 1.0) < 0.001

    def test_flow_to_tcp_sums_to_100(self):
        primary = {"ALP": 38.0, "LIB": 35.0, "GRN": 14.0, "IND": 10.0, "informal": 3.0}
        tcp = self.model.flow_to_tcp(primary, self.model.default_pref_flows())
        assert abs(tcp["ALP"] + tcp["LIB"] - 100.0) < 0.1

    def test_flow_to_tcp_alp_wins(self):
        # High GRN and IND prefs to ALP should push ALP above 50%
        primary = {"ALP": 38.0, "LIB": 30.0, "GRN": 18.0, "IND": 11.0, "informal": 3.0}
        pref_matrix = {"GRN": {"ALP": 0.80, "LIB": 0.20}, "IND": {"ALP": 0.60, "LIB": 0.40}}
        tcp = self.model.flow_to_tcp(primary, pref_matrix)
        assert tcp["ALP"] > 50.0

    def test_adjust_preference_flow(self):
        self.model.adjust_preference_flow("GRN", "ALP", 80.0)
        assert abs(self.model._pref_flows["GRN"]["ALP"] - 0.80) < 0.001
        assert abs(self.model._pref_flows["GRN"]["LIB"] - 0.20) < 0.001

    def test_adjust_flow_complements_to_one(self):
        self.model.adjust_preference_flow("IND", "ALP", 65.0)
        total = self.model._pref_flows["IND"]["ALP"] + self.model._pref_flows["IND"]["LIB"]
        assert abs(total - 1.0) < 0.001

    def test_exhaustion_rate_is_zero(self):
        assert self.model.calculate_exhaustion_rate() == 0.0

    def test_three_way_resolution(self):
        votes = {"ALP": 38.0, "LIB": 35.0, "GRN": 14.0}
        eliminated, remaining = self.model.three_way_contest_resolution(votes)
        assert eliminated == "GRN"
        assert "ALP" in remaining
        assert "LIB" in remaining

    def test_three_way_correct_remaining(self):
        votes = {"ALP": 10.0, "LIB": 50.0, "GRN": 40.0}
        eliminated, remaining = self.model.three_way_contest_resolution(votes)
        assert eliminated == "ALP"
