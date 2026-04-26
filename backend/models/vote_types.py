"""Vote types dataclass."""
from dataclasses import dataclass


@dataclass
class VoteTypes:
    ordinary: int = 0
    pre_poll: int = 0
    postal: int = 0
    absent: int = 0
    provisional: int = 0

    @property
    def total(self) -> int:
        return self.ordinary + self.pre_poll + self.postal + self.absent + self.provisional

    @classmethod
    def from_dict(cls, d: dict) -> "VoteTypes":
        return cls(
            ordinary=int(d.get("ordinary_booth", d.get("ordinary", 0))),
            pre_poll=int(d.get("pre_poll", 0)),
            postal=int(d.get("postal", 0)),
            absent=int(d.get("absent", 0)),
            provisional=int(d.get("provisional", 0)),
        )
