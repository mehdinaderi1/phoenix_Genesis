from dataclasses import dataclass, field
from datetime import datetime, UTC


@dataclass(slots=True)
class EvolutionRecord:

    strategy: str

    parent: str | None

    generation: int

    decision: str

    reason: str

    score: float

    success_rate: float

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(UTC)
    )


class StrategyEvolutionHistory:

    def __init__(self):

        self._history = []

    def add(self, record: EvolutionRecord):

        self._history.append(record)

    def all(self):

        return list(self._history)

    def latest(self):

        if not self._history:
            return None

        return self._history[-1]

    def by_strategy(
        self,
        strategy
    ):

        return [

            r

            for r in self._history

            if r.strategy == strategy

        ]