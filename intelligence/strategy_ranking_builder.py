from datetime import datetime

from intelligence.ranked_strategy_item import RankedStrategyItem
from intelligence.strategy_ranking_result import StrategyRankingResult


class StrategyRankingBuilder:


    def build(
        self,
        ranked_strategies,
        market_context=None
    ):

        if market_context is None:

            market_context = {}


        items = []


        for index, strategy in enumerate(
            ranked_strategies,
            start=1
        ):

            item = RankedStrategyItem(

                strategy_record=strategy,

                strategy_name=strategy.get(
                    "strategy",
                    "UNKNOWN"
                ),

                rank=index,

                final_score=strategy.get(
                    "score",
                    0
                ),

                confidence=self._confidence(
                    strategy
                ),

                score_breakdown={

                    "score":
                        strategy.get(
                            "score",
                            0
                        ),

                    "success_rate":
                        strategy.get(
                            "success_rate",
                            0
                        ),

                    "samples":
                        strategy.get(
                            "samples",
                            0
                        )

                },

                reasons=self._reasons(
                    strategy
                )
            )


            items.append(item)


        top_strategy = None


        if items:

            top_strategy = items[0]


        return StrategyRankingResult(

            ranked_strategies=items,

            top_strategy=top_strategy,

            ranking_explanation=self._explanation(
                top_strategy
            ),

            market_context=market_context,

            timestamp=datetime.now()

        )


    def _confidence(
        self,
        strategy
    ):

        success_rate = strategy.get(
            "success_rate",
            0
        )

        return min(
            success_rate / 100,
            1
        )


    def _reasons(
        self,
        strategy
    ):

        reasons = []


        if strategy.get("score", 0) > 80:

            reasons.append(
                "Strong performance score"
            )


        if strategy.get("success_rate", 0) > 70:

            reasons.append(
                "High historical success rate"
            )


        if not reasons:

            reasons.append(
                "Ranked based on available metrics"
            )


        return reasons


    def _explanation(
        self,
        top_strategy
    ):

        if not top_strategy:

            return "No strategy ranked."


        return (
            "Top strategy ranked because "
            "it achieved the highest available score."
        )