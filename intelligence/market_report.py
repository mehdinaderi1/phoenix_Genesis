from dataclasses import dataclass


@dataclass
class MarketReport:
    symbol: str

    trend: str
    momentum: str
    regime: str

    risk_level: str

    confidence: float

    reasoning: str


    def summary(self):
        return {
            "symbol": self.symbol,
            "trend": self.trend,
            "momentum": self.momentum,
            "regime": self.regime,
            "risk_level": self.risk_level,
            "confidence": self.confidence,
            "reasoning": self.reasoning
        }