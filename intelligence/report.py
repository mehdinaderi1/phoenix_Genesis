from dataclasses import dataclass
from typing import List


@dataclass
class MarketReport:
    symbol: str
    timeframe: str
    trend: str
    signal: str
    confidence: float
    risk: str
    reasons: List[str]

    def summary(self):
        return {
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "trend": self.trend,
            "signal": self.signal,
            "confidence": self.confidence,
            "risk": self.risk,
            "reasons": self.reasons
        }