from dataclasses import dataclass


@dataclass
class PatternConfidence:

    regime: str

    action: str

    confidence: float

    reliability: str

    samples: int

    score: float