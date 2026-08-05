from dataclasses import dataclass


@dataclass
class RankedStrategyItem:

    strategy_record: dict

    strategy_name: str

    rank: int

    final_score: float

    confidence: float

    score_breakdown: dict

    reasons: list[str]