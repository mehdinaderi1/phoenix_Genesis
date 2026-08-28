from dataclasses import dataclass


@dataclass
class MetaFeedbackRecord:

    confidence_before: float

    adjustment: float

    confidence_after: float

    outcome: str

    meta_effective: bool