from dataclasses import dataclass


@dataclass
class MarketRegime:

    regime: str
    confidence: float
    reasons: list