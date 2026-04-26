"""Candidate dataclass."""
from dataclasses import dataclass


@dataclass
class Candidate:
    candidate_id: str
    name: str
    party: str
    party_abbrev: str
    colour: str

    @classmethod
    def from_dict(cls, d: dict) -> "Candidate":
        return cls(
            candidate_id=d["candidate_id"],
            name=d["name"],
            party=d["party"],
            party_abbrev=d["party_abbrev"],
            colour=d.get("colour", "#757575"),
        )
