"""Tests for backend/ingestion modules."""
import json
import pytest
import pandas as pd
from pathlib import Path

from backend.ingestion.csv_loader import (
    load_candidates,
    load_booths,
    load_live_count,
    load_declaration_votes,
    load_historical_booths,
)
from backend.ingestion.aec_loader import (
    load_election_config,
    validate_config,
    parse_tcp_candidates,
)
from backend.ingestion.booth_loader import merge_booth_data, calculate_booth_progress

# Path to sample data
SAMPLE_DIR = Path(__file__).parent.parent / "data" / "sample"


class TestCsvLoader:
    def test_load_candidates(self):
        candidates = load_candidates(str(SAMPLE_DIR / "candidates.csv"))
        assert len(candidates) == 4
        assert candidates[0].candidate_id == "chen_sarah"
        assert candidates[0].party_abbrev == "ALP"

    def test_load_candidates_missing_file(self):
        candidates = load_candidates("/nonexistent/path/candidates.csv")
        assert candidates == []

    def test_load_booths(self):
        booths = load_booths(str(SAMPLE_DIR / "booths.csv"))
        assert len(booths) == 8
        assert booths[0].booth_id == "booth_001"
        assert isinstance(booths[0].lat, float)
        assert isinstance(booths[0].lon, float)

    def test_load_booths_missing_file(self):
        booths = load_booths("/nonexistent/path/booths.csv")
        assert booths == []

    def test_load_live_count(self):
        df = load_live_count(str(SAMPLE_DIR / "live_count.csv"))
        assert not df.empty
        assert "booth_id" in df.columns
        assert "chen_sarah_tcp" in df.columns

    def test_load_live_count_missing_file(self):
        df = load_live_count("/nonexistent/path/live_count.csv")
        assert df.empty

    def test_load_declaration_votes(self):
        df = load_declaration_votes(str(SAMPLE_DIR / "declaration_votes.csv"))
        assert not df.empty
        assert "vote_type" in df.columns
        assert "estimated_total" in df.columns

    def test_load_historical_booths(self):
        df = load_historical_booths(str(SAMPLE_DIR / "historical_booths.csv"))
        assert not df.empty
        assert "booth_id" in df.columns
        assert "alp_tcp_pct" in df.columns


class TestAecLoader:
    def test_load_election_config(self):
        election = load_election_config(str(SAMPLE_DIR / "election_config.json"))
        assert election.electorate == "Banksia"
        assert election.state == "Victoria"
        assert election.enrolled_voters == 35420
        assert len(election.tcp_candidates) == 2

    def test_validate_config_valid(self):
        with open(SAMPLE_DIR / "election_config.json") as f:
            config = json.load(f)
        assert validate_config(config) is True

    def test_validate_config_missing_field(self):
        config = {"election_id": "test"}  # Missing many required fields
        assert validate_config(config) is False

    def test_validate_config_wrong_tcp_count(self):
        with open(SAMPLE_DIR / "election_config.json") as f:
            config = json.load(f)
        config["tcp_candidates"] = ["only_one"]
        assert validate_config(config) is False

    def test_parse_tcp_candidates(self):
        election = load_election_config(str(SAMPLE_DIR / "election_config.json"))
        cand_a, cand_b = parse_tcp_candidates(election)
        assert cand_a == "chen_sarah"
        assert cand_b == "morrison_james"


class TestBoothLoader:
    def test_merge_booth_data(self):
        live_df = load_live_count(str(SAMPLE_DIR / "live_count.csv"))
        hist_df = load_historical_booths(str(SAMPLE_DIR / "historical_booths.csv"))
        merged = merge_booth_data(live_df, hist_df)
        assert not merged.empty
        assert "booth_id" in merged.columns

    def test_merge_empty_historical(self):
        live_df = load_live_count(str(SAMPLE_DIR / "live_count.csv"))
        merged = merge_booth_data(live_df, pd.DataFrame())
        assert not merged.empty

    def test_merge_empty_live(self):
        hist_df = load_historical_booths(str(SAMPLE_DIR / "historical_booths.csv"))
        merged = merge_booth_data(pd.DataFrame(), hist_df)
        assert merged.empty

    def test_calculate_booth_progress(self):
        live_df = load_live_count(str(SAMPLE_DIR / "live_count.csv"))
        result = calculate_booth_progress(live_df)
        assert "total_primary_counted" in result.columns
        assert "counted_pct" in result.columns

    def test_counted_pct_range(self):
        live_df = load_live_count(str(SAMPLE_DIR / "live_count.csv"))
        result = calculate_booth_progress(live_df)
        assert result["counted_pct"].between(0, 100).all()
