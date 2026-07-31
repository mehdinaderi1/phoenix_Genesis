from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class EvolutionRecord:
    parent: str
    child: str
    generation: int
    reason: str
    score_before: float
    score_after: float
    timestamp: datetime


class EvolutionHistory:

    def __init__(self):
        self._records = []

    def add(self, record: EvolutionRecord):
        self._records.append(record)

    def all(self):
        return list(self._records)

    def get_all(self):
        return list(self._records)

    def latest(self):
        if not self._records:
            return None
        return self._records[-1]

    def children_of(self, parent):
        return [
            r for r in self._records
            if r.parent == parent
        ]