from dataclasses import dataclass
from typing import List


@dataclass
class MarketReport:
    symbol: str
    timeframe: str
    trend: str
    regime: str
    signal: str
    confidence: float
    risk: str
    reasons: List[str]
    decision: object = None
    action_proposal: object = None

    def summary(self):
        return {
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "trend": self.trend,
            "regime": self.regime,
            "signal": self.signal,
            "confidence": self.confidence,
            "risk": self.risk,
            "reasons": self.reasons
        }