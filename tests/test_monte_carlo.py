"""Tests for backend/analysis/monte_carlo.py"""
import pytest
import numpy as np

from backend.analysis.monte_carlo import MonteCarloEngine


class TestMonteCarloEngine:
    def setup_method(self):
        self.engine = MonteCarloEngine(base_margin=800, std_dev=1500)

    def test_simulation_shape(self):
        results = self.engine.run_simulation(n_iterations=1000)
        assert len(results) == 1000

    def test_simulation_distribution(self):
        results = self.engine.run_simulation(n_iterations=10000)
        # Mean should be close to base_margin
        assert abs(results.mean() - 800) < 150  # within 150 votes

    def test_simulation_std(self):
        results = self.engine.run_simulation(n_iterations=10000)
        assert abs(results.std() - 1500) < 200

    def test_probability_alp_range(self):
        results = self.engine.run_simulation(10000)
        prob = self.engine.probability_of_victory(results, "ALP")
        assert 0.0 <= prob <= 1.0

    def test_probability_large_positive_margin(self):
        engine = MonteCarloEngine(base_margin=10000, std_dev=500)
        results = engine.run_simulation(10000)
        prob = engine.probability_of_victory(results, "ALP")
        assert prob > 0.99

    def test_probability_large_negative_margin(self):
        engine = MonteCarloEngine(base_margin=-10000, std_dev=500)
        results = engine.run_simulation(10000)
        prob = engine.probability_of_victory(results, "ALP")
        assert prob < 0.01

    def test_probability_alp_plus_lib_equals_one(self):
        results = self.engine.run_simulation(10000)
        alp_prob = self.engine.probability_of_victory(results, "ALP")
        lib_prob = self.engine.probability_of_victory(results, "LIB")
        # Ignores ties (margin == 0), so approximately 1
        assert abs(alp_prob + lib_prob - 1.0) < 0.01

    def test_confidence_interval_order(self):
        results = self.engine.run_simulation(10000)
        low, high = self.engine.confidence_interval(results, 0.95)
        assert low < high

    def test_confidence_interval_contains_mean(self):
        results = self.engine.run_simulation(10000)
        low, high = self.engine.confidence_interval(results, 0.95)
        assert low < results.mean() < high

    def test_confidence_interval_width_vs_level(self):
        results = self.engine.run_simulation(10000)
        lo_80, hi_80 = self.engine.confidence_interval(results, 0.80)
        lo_95, hi_95 = self.engine.confidence_interval(results, 0.95)
        assert (hi_95 - lo_95) > (hi_80 - lo_80)

    def test_generate_scenarios_count(self):
        scenarios = self.engine.generate_scenarios(n=50)
        assert len(scenarios) == 50

    def test_generate_scenarios_structure(self):
        scenarios = self.engine.generate_scenarios(n=5)
        for s in scenarios:
            assert "scenario_id" in s
            assert "projected_margin" in s
            assert "alp_wins" in s
            assert isinstance(s["alp_wins"], bool)
