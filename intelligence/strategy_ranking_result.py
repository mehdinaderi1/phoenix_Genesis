from dataclasses import dataclass
from datetime import datetime

from intelligence.ranked_strategy_item import RankedStrategyItem


@dataclass
class StrategyRankingResult:

    ranked_strategies: list[RankedStrategyItem]

    top_strategy: RankedStrategyItem | None

    ranking_explanation: str

    market_context: dict

    timestamp: datetime