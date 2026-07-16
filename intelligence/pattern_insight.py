from dataclasses import dataclass


@dataclass
class PatternInsight:

    matched_pattern: str

    confidence: float

    samples: int

    reliability: str