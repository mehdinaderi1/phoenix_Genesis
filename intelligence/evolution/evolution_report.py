from dataclasses import dataclass


@dataclass
class EvolutionReport:

    total_evolutions: int

    best_strategy: str | None

    average_improvement: float

    strongest_rank: str

    success_rate: float

    explanation: dict | None = None