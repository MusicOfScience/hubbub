"""Poll aggregation with exponential decay weighting."""
import math
from datetime import date, datetime
from typing import Dict, List


class PollAggregator:
    """Aggregate polls with recency weighting and house effects."""

    def __init__(self):
        self._polls: List[dict] = []
        self._house_effects: Dict[str, dict] = {}

    def add_poll(self, poll_data: dict):
        """
        Add a poll.
        poll_data keys: date (str YYYY-MM-DD), pollster, alp, lib, grn, ind, others
        """
        self._polls.append(poll_data)

    def weighted_average(self, half_life_days: int = 14) -> dict:
        """
        Compute exponential decay weighted average of polls.
        More recent polls get higher weight.
        """
        if not self._polls:
            return {"ALP": 0.0, "LIB": 0.0, "GRN": 0.0, "IND": 0.0, "OTH": 0.0}

        today = date.today()
        keys = ["alp", "lib", "grn", "ind", "others"]
        weighted_sums = {k: 0.0 for k in keys}
        total_weight = 0.0

        for poll in self._polls:
            poll_date = datetime.strptime(str(poll["date"]), "%Y-%m-%d").date()
            days_ago = (today - poll_date).days
            weight = math.exp(-days_ago * math.log(2) / half_life_days)

            # Apply house effect adjustment
            pollster = poll.get("pollster", "unknown")
            effect = self._house_effects.get(pollster, {})

            for k in keys:
                val = float(poll.get(k, 0)) + float(effect.get(k, 0))
                weighted_sums[k] += val * weight
            total_weight += weight

        if total_weight == 0:
            return {"ALP": 0.0, "LIB": 0.0, "GRN": 0.0, "IND": 0.0, "OTH": 0.0}

        result = {k: round(weighted_sums[k] / total_weight, 1) for k in keys}
        return {
            "ALP": result["alp"],
            "LIB": result["lib"],
            "GRN": result["grn"],
            "IND": result["ind"],
            "OTH": result["others"],
        }

    def house_effect_adjustment(self, pollster_id: str, adjustment: dict):
        """Store house effect adjustments for a pollster."""
        self._house_effects[pollster_id] = adjustment

    def get_aggregated_primary_votes(self) -> dict:
        """Return aggregated primary votes using default half-life."""
        return self.weighted_average()
