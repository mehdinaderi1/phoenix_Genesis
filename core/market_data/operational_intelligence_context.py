from dataclasses import dataclass


@dataclass(frozen=True)
class OperationalIntelligenceContext:
    """Consensus-compatible context for operational intelligence."""

    symbol: str
    trend: str
    signal: str
    confidence: float
    consensus_breakdown: dict | None = None

    def summary(self):
        result = {
            "symbol": self.symbol,
            "trend": self.trend,
            "signal": self.signal,
            "confidence": self.confidence
        }

        if self.consensus_breakdown is not None:
            result["consensus_breakdown"] = self.consensus_breakdown

        return result
