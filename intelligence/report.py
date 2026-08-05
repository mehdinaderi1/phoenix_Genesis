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
    historical_context: object | None = None
    intelligence_context: object | None = None
    evolution: dict | None = None
    champion_strategy: dict | None = None
    strategy_intelligence: object | None = None	

    def __contains__(self, key):
        return hasattr(self, key)

    def __getitem__(self, key):
        return getattr(self, key)


    def keys(self):
        return self.__dict__.keys()


    def get(self, key, default=None):
        return getattr(self, key, default)


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