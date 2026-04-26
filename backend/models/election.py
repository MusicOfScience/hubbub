"""Election dataclass."""
from dataclasses import dataclass, field
from datetime import date
from typing import List, Dict, Optional


@dataclass
class Election:
    election_id: str
    electorate: str
    state: str
    level: str
    election_date: str
    enrolled_voters: int
    tcp_candidates: List[str]
    candidates: List[dict] = field(default_factory=list)
    vote_type_estimates: Dict[str, int] = field(default_factory=dict)
    previous_election_date: Optional[str] = None

    @classmethod
    def from_dict(cls, d: dict) -> "Election":
        return cls(
            election_id=d["election_id"],
            electorate=d["electorate"],
            state=d["state"],
            level=d["level"],
            election_date=d["election_date"],
            enrolled_voters=d["enrolled_voters"],
            tcp_candidates=d.get("tcp_candidates", []),
            candidates=d.get("candidates", []),
            vote_type_estimates=d.get("vote_type_estimates", {}),
            previous_election_date=d.get("previous_election_date"),
        )

    def total_estimated_votes(self) -> int:
        return sum(self.vote_type_estimates.values())
