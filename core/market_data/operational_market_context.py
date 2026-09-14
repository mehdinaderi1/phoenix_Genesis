from dataclasses import dataclass


@dataclass(frozen=True)
class OperationalMarketContext:
    symbol: str
    trend: str
    signal: str
    confidence: float
    timestamp: str

    def summary(self):
        return {
            "symbol": self.symbol,
            "trend": self.trend,
            "signal": self.signal,
            "confidence": self.confidence,
            "timestamp": self.timestamp
        }
