from dataclasses import dataclass


@dataclass
class ConsensusResult:
    trend: str
    signal: str
    confidence: float
    breakdown: dict | None = None
    reason_code: str | None = None

    def summary(self):
        return {
            "trend": self.trend,
            "signal": self.signal,
            "confidence": self.confidence,
            "reason_code": self.reason_code,
        }