"""Tests for backend/analysis/swing.py"""
import pytest
import pandas as pd

from backend.analysis.swing import (
    calculate_primary_swing,
    calculate_tcp_swing,
    booth_level_swings,
    apply_swing_scenario,
    weighted_swing,
)


class TestCalculatePrimarySwing:
    def test_positive_swing(self):
        assert calculate_primary_swing(40.0, 35.0) == 5.0

    def test_negative_swing(self):
        assert calculate_primary_swing(32.0, 38.0) == -6.0

    def test_zero_swing(self):
        assert calculate_primary_swing(38.0, 38.0) == 0.0

    def test_rounding(self):
        result = calculate_primary_swing(38.123, 35.456)
        assert result == round(38.123 - 35.456, 2)


class TestCalculateTcpSwing:
    def test_alp_gaining(self):
        assert calculate_tcp_swing(52.5, 50.0) == 2.5

    def test_alp_losing(self):
        assert calculate_tcp_swing(48.0, 52.0) == -4.0


class TestBoothLevelSwings:
    def make_current_df(self):
        return pd.DataFrame({
            "booth_id": ["b1", "b2"],
            "alp_primary_pct_curr": [38.5, 36.0],
            "lib_primary_pct_curr": [34.5, 37.0],
            "alp_tcp_pct_curr": [52.0, 50.5],
        })

    def make_hist_df(self):
        return pd.DataFrame({
            "booth_id": ["b1", "b2"],
            "alp_primary_pct_hist": [35.8, 34.2],
            "lib_primary_pct_hist": [37.1, 38.5],
            "alp_tcp_pct_hist": [49.5, 48.0],
        })

    def test_swing_calculated(self):
        curr = self.make_current_df()
        hist = self.make_hist_df()
        result = booth_level_swings(curr, hist)
        assert "alp_swing" in result.columns
        assert len(result) == 2

    def test_tcp_swing_calculated(self):
        curr = self.make_current_df()
        hist = self.make_hist_df()
        result = booth_level_swings(curr, hist)
        assert "alp_tcp_swing" in result.columns
        assert result.loc[0, "alp_tcp_swing"] == round(52.0 - 49.5, 2)

    def test_empty_returns_empty(self):
        result = booth_level_swings(pd.DataFrame(), pd.DataFrame())
        assert result.empty


class TestApplySwingScenario:
    def test_positive_swing(self):
        base = {"ALP": 38.0, "LIB": 35.0, "GRN": 14.0, "IND": 10.0}
        swings = {"ALP": 2.0, "LIB": -2.0}
        result = apply_swing_scenario(base, swings)
        # ALP should increase, LIB should decrease
        assert result["ALP"] > base["ALP"]
        assert result["LIB"] < base["LIB"]

    def test_zero_swings(self):
        base = {"ALP": 38.0, "LIB": 35.0, "GRN": 14.0}
        result = apply_swing_scenario(base, {})
        assert result["ALP"] == base["ALP"]

    def test_values_positive(self):
        base = {"ALP": 38.0, "LIB": 35.0}
        swings = {"ALP": -50.0}  # extreme swing
        result = apply_swing_scenario(base, swings)
        for v in result.values():
            assert v >= 0.0

    def test_preserves_total(self):
        base = {"ALP": 38.0, "LIB": 35.0, "GRN": 14.0, "IND": 10.0}
        original_total = sum(base.values())
        swings = {"ALP": 2.0, "LIB": -2.0}
        result = apply_swing_scenario(base, swings)
        assert abs(sum(result.values()) - original_total) < 0.01


class TestWeightedSwing:
    def test_equal_weights(self):
        swings = [2.0, 4.0]
        weights = [1.0, 1.0]
        result = weighted_swing(swings, weights)
        assert result == 3.0

    def test_unequal_weights(self):
        swings = [0.0, 4.0]
        weights = [3.0, 1.0]
        result = weighted_swing(swings, weights)
        assert result == 1.0

    def test_empty_lists(self):
        assert weighted_swing([], []) == 0.0

    def test_zero_weights(self):
        assert weighted_swing([1.0, 2.0], [0.0, 0.0]) == 0.0
