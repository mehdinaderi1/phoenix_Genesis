from dataclasses import dataclass


@dataclass
class RiskAssessment:

    level: str
    score: float
    reasons: list