from dataclasses import dataclass


@dataclass
class IntelligenceReport:

    total_decisions: int

    approval_rate: float

    average_confidence: float

    average_quality: float

    best_action: str | None

    best_regime: str | None