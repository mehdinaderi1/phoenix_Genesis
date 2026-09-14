from dataclasses import dataclass


@dataclass(frozen=True)
class OperationalIntelligenceContext:
    """Consensus-compatible context for operational intelligence."""

    symbol: str
    trend: str
    signal: str
    confidence: float

    def summary(self):
        return {
            "symbol": self.symbol,
            "trend": self.trend,
            "signal": self.signal,
            "confidence": self.confidence
        }
