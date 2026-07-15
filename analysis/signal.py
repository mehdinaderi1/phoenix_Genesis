from dataclasses import dataclass
from typing import List


@dataclass
class Signal:
    symbol: str
    action: str
    confidence: float
    reasons: List[str]

    def summary(self):
        return {
            "symbol": self.symbol,
            "action": self.action,
            "confidence": self.confidence,
            "reasons": self.reasons
        }