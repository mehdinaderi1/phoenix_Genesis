from dataclasses import dataclass


@dataclass
class HistoricalInsight:

    pattern: str

    samples: int

    average_confidence: float

    average_quality: float

    reliability: str