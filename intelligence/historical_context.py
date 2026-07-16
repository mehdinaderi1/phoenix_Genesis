from dataclasses import dataclass


@dataclass
class HistoricalContext:

    pattern: str

    confidence: float

    samples: int

    reliability: str