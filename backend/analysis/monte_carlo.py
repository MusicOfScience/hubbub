"""Monte Carlo simulation engine for election prediction."""
from typing import List

import numpy as np


class MonteCarloEngine:
    """Run Monte Carlo simulations of election outcomes."""

    def __init__(self, base_margin: int, std_dev: int = 1500):
        self.base_margin = base_margin
        self.std_dev = std_dev

    def run_simulation(self, n_iterations: int = 10000) -> np.ndarray:
        """
        Run simulation. Positive results = ALP wins, negative = LIB wins.
        Returns array of margin outcomes.
        """
        rng = np.random.default_rng()
        return rng.normal(loc=self.base_margin, scale=self.std_dev, size=n_iterations)

    def probability_of_victory(self, results: np.ndarray, candidate: str = "ALP") -> float:
        """
        Return fraction of simulations won by the specified candidate.
        Positive margin = ALP wins by convention.
        """
        if candidate.upper() == "ALP":
            return float(np.mean(results > 0))
        else:
            return float(np.mean(results < 0))

    def confidence_interval(self, results: np.ndarray, level: float = 0.95) -> tuple:
        """Return (lower, upper) confidence interval for the margin distribution."""
        alpha = 1.0 - level
        lower = float(np.percentile(results, alpha / 2 * 100))
        upper = float(np.percentile(results, (1 - alpha / 2) * 100))
        return (round(lower), round(upper))

    def generate_scenarios(self, n: int = 100) -> List[dict]:
        """
        Generate n scenario dicts with varied parameters.
        """
        rng = np.random.default_rng()
        scenarios = []
        for i in range(n):
            swing_variation = rng.normal(0, 1.5)
            pref_variation = rng.normal(0, 2.0)
            margin = int(self.base_margin + swing_variation * 500 + pref_variation * 200)
            scenarios.append({
                "scenario_id": i + 1,
                "swing_variation": round(swing_variation, 2),
                "pref_variation": round(pref_variation, 2),
                "projected_margin": margin,
                "alp_wins": margin > 0,
            })
        return scenarios
