from intelligence.strategy_selector import StrategySelector
from intelligence.strategy_ranking_result import StrategyRankingResult
from intelligence.ranked_strategy_item import RankedStrategyItem
from datetime import datetime



class MockRecall:


    def recall(
        self,
        regime,
        signal,
        risk
    ):

        return [

            {
                "strategy": "weak_strategy",
                "score": 50,
                "status": "ACTIVE"
            },

            {
                "strategy": "champion_strategy",
                "score": 95,
                "status": "ACTIVE"
            }

        ]



class RankingResultOnlyRanker:


    def rank_with_result(
        self,
        strategies,
        market_context=None
    ):

        champion = RankedStrategyItem(

            strategy_record={
                "strategy": "champion_strategy",
                "score": 95,
                "status": "ACTIVE"
            },

            strategy_name="champion_strategy",

            rank=1,

            final_score=95,

            confidence=0.95,

            score_breakdown={
                "score": 95
            },

            reasons=[
                "Highest ranked strategy"
            ]

        )


        return StrategyRankingResult(

            ranked_strategies=[
                champion
            ],

            top_strategy=champion,

            ranking_explanation=(
                "Champion selected by ranking intelligence"
            ),

            market_context=(
                market_context or {}
            ),

            timestamp=datetime.now()

        )



def test_selector_uses_strategy_ranking_result():


    selector = StrategySelector(

        strategy_recall=MockRecall(),

        strategy_ranking=RankingResultOnlyRanker()

    )


    result = selector.select(

        "TREND",

        "BUY",

        "LOW"

    )


    assert result is not None


    assert result["strategy"] == "champion_strategy"


    assert result["score"] == 95