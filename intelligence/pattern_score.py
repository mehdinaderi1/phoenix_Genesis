from dataclasses import dataclass


@dataclass
class PatternScore:

    regime: str

    action: str

    samples: int

    average_quality: float

    reliability: str

    score: float

    rank: int