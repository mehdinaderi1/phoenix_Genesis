from dataclasses import dataclass


@dataclass
class DecisionResult:

    action: str
    reason: str
    confidence: float