"""Booth dataclass."""
from dataclasses import dataclass
from typing import Optional


@dataclass
class Booth:
    booth_id: str
    name: str
    lat: float
    lon: float
    enrolled: int
    division: str

    @classmethod
    def from_dict(cls, d: dict) -> "Booth":
        return cls(
            booth_id=str(d["booth_id"]),
            name=d["booth_name"],
            lat=float(d["lat"]),
            lon=float(d["lon"]),
            enrolled=int(d["enrolled"]),
            division=d.get("division", ""),
        )
