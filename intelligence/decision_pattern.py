from dataclasses import dataclass


@dataclass
class DecisionPattern:

    regime: str

    action: str

    samples: int

    average_quality: float