from dataclasses import dataclass


@dataclass
class ConsensusResult:
    trend: str
    signal: str
    confidence: float

    def summary(self):
        return {
            "trend": self.trend,
            "signal": self.signal,
            "confidence": self.confidence
        }