from dataclasses import dataclass


@dataclass
class IntelligenceContext:

    learning_insight: object | None = None

    historical_context: object | None = None

    pattern_insight: object | None = None

    quality_score: int = 0

    adaptive_confidence: int = 0