from dataclasses import dataclass


@dataclass
class StrategyDecisionAssessment:

    strategy_name: str

    confidence: float

    approved: bool

    historical_valid: bool

    governance_status: str

    reasons: list[str]

    warnings: list[str]