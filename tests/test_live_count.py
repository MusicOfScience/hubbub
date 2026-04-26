"""Tests for backend/analysis/live_count.py"""
import pytest
import pandas as pd

from backend.analysis.live_count import (
    calculate_tcp_margin,
    calculate_count_progress,
    estimate_outstanding_votes,
    project_final_margin,
    recount_risk,
    count_status,
    required_vote_share,
)


def make_booth_df(chen_tcp, morrison_tcp):
    """Create a sample booth results DataFrame."""
    return pd.DataFrame({
        "booth_id": ["booth_001", "booth_002"],
        "chen_sarah_primary": [600, 500],
        "morrison_james_primary": [540, 480],
        "chen_sarah_tcp": chen_tcp,
        "morrison_james_tcp": morrison_tcp,
        "total_enrolled": [4200, 3800],
        "counted_flag": [1, 1],
    })


class TestCalculateTcpMargin:
    def test_alp_ahead(self):
        df = make_booth_df([900, 800], [600, 550])
        margin, pct = calculate_tcp_margin(df)
        assert margin == 550  # (900+800) - (600+550)
        assert margin > 0

    def test_lib_ahead(self):
        df = make_booth_df([500, 450], [800, 750])
        margin, pct = calculate_tcp_margin(df)
        assert margin < 0

    def test_empty_df(self):
        margin, pct = calculate_tcp_margin(pd.DataFrame())
        assert margin == 0
        assert pct == 0.0

    def test_pct_range(self):
        df = make_booth_df([700, 600], [700, 600])
        margin, pct = calculate_tcp_margin(df)
        assert margin == 0
        assert pct == 0.0

    def test_returns_int_margin(self):
        df = make_booth_df([892, 791], [615, 538])
        margin, _ = calculate_tcp_margin(df)
        assert isinstance(margin, int)


class TestCalculateCountProgress:
    def test_fifty_percent(self):
        pct = calculate_count_progress(500, 1000)
        assert pct == 50.0

    def test_zero_counted(self):
        pct = calculate_count_progress(0, 1000)
        assert pct == 0.0

    def test_full_count(self):
        pct = calculate_count_progress(1000, 1000)
        assert pct == 100.0

    def test_over_enrolled(self):
        # Should cap at 100
        pct = calculate_count_progress(1100, 1000)
        assert pct == 100.0

    def test_zero_total(self):
        pct = calculate_count_progress(0, 0)
        assert pct == 0.0


class TestEstimateOutstandingVotes:
    def make_decl_df(self):
        return pd.DataFrame({
            "vote_type": ["postal", "pre_poll", "absent"],
            "estimated_total": [4500, 9000, 1500],
            "received_count": [1200, 3100, 400],
            "alp_lean_pct": [46, 52, 51],
            "lib_lean_pct": [54, 48, 49],
        })

    def test_calculates_outstanding(self):
        decl_df = self.make_decl_df()
        result = estimate_outstanding_votes(decl_df, pd.DataFrame())
        assert result["postal"] == 3300  # 4500 - 1200
        assert result["pre_poll"] == 5900  # 9000 - 3100
        assert result["absent"] == 1100

    def test_empty_decl(self):
        result = estimate_outstanding_votes(pd.DataFrame(), pd.DataFrame())
        assert result == {}

    def test_no_negative_outstanding(self):
        df = pd.DataFrame({
            "vote_type": ["postal"],
            "estimated_total": [100],
            "received_count": [150],  # More received than estimated
            "alp_lean_pct": [46],
            "lib_lean_pct": [54],
        })
        result = estimate_outstanding_votes(df, pd.DataFrame())
        assert result["postal"] == 0


class TestReCountRisk:
    def test_high_risk(self):
        level, threshold = recount_risk(50)
        assert level == "high"
        assert threshold == 100

    def test_high_risk_negative(self):
        level, _ = recount_risk(-50)
        assert level == "high"

    def test_moderate_risk(self):
        level, threshold = recount_risk(250)
        assert level == "moderate"
        assert threshold == 500

    def test_low_risk(self):
        level, _ = recount_risk(1000)
        assert level == "low"

    def test_exactly_at_threshold(self):
        level, _ = recount_risk(100)
        # 100 is NOT < 100, so moderate
        assert level == "moderate"


class TestCountStatus:
    def test_early(self):
        assert count_status(10.0) == "early"
        assert count_status(0.0) == "early"
        assert count_status(24.9) == "early"

    def test_developing(self):
        assert count_status(25.0) == "developing"
        assert count_status(49.9) == "developing"

    def test_mature(self):
        assert count_status(50.0) == "mature"
        assert count_status(74.9) == "mature"

    def test_near_final(self):
        assert count_status(75.0) == "near-final"
        assert count_status(100.0) == "near-final"


class TestRequiredVoteShare:
    def test_trailing_needs_more_than_50(self):
        current = {"ALP": 10000, "LIB": 9000}
        outstanding = {"postal": 2000, "pre_poll": 1000}
        req = required_vote_share(current, outstanding)
        assert req > 50.0

    def test_no_outstanding(self):
        current = {"ALP": 10000, "LIB": 9000}
        req = required_vote_share(current, {})
        assert req == 100.0

    def test_result_in_range(self):
        current = {"ALP": 5000, "LIB": 5000}
        outstanding = {"postal": 1000}
        req = required_vote_share(current, outstanding)
        assert 0.0 <= req <= 100.0
