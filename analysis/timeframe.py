from dataclasses import dataclass


@dataclass
class TimeframeAnalysis:
    timeframe: str
    trend: str
    signal: str
    confidence: float
    reasons: tuple[str, ...] = ()

    def summary(self):
        return {
            "timeframe": self.timeframe,
            "trend": self.trend,
            "signal": self.signal,
            "confidence": self.confidence
        }
