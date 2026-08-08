from intelligence.strategy_council import StrategyCouncil
from intelligence.strategy_ranking_result import StrategyRankingResult
from intelligence.ranked_strategy_item import RankedStrategyItem
from datetime import datetime


def test_strategy_council_evaluates_ranking_result():

    ranked_strategies = [

        RankedStrategyItem(
            strategy_record={
                "strategy": "trend_following",
                "action": "BUY",
                "confidence": 90
            },
            strategy_name="trend_following",
            rank=1,
            final_score=90,
            confidence=0.9,
            score_breakdown={},
            reasons=[]
        ),

        RankedStrategyItem(
            strategy_record={
                "strategy": "breakout_strategy",
                "action": "BUY",
                "confidence": 80
            },
            strategy_name="breakout_strategy",
            rank=2,
            final_score=80,
            confidence=0.8,
            score_breakdown={},
            reasons=[]
        ),

        RankedStrategyItem(
            strategy_record={
                "strategy": "mean_reversion",
                "action": "WAIT",
                "confidence": 60
            },
            strategy_name="mean_reversion",
            rank=3,
            final_score=60,
            confidence=0.6,
            score_breakdown={},
            reasons=[]
        )
    ]


    ranking_result = StrategyRankingResult(
        ranked_strategies=ranked_strategies,
        top_strategy=ranked_strategies[0],
        ranking_explanation="test ranking",
        market_context={
            "regime": "bullish"
        },
        timestamp=datetime.now()
    )


    council = StrategyCouncil()


    result = council.evaluate(
        ranking_result
    )


    assert result is not None

    assert result["decision"] == "BUY"

    assert result["supporting_strategies"] == 2

    assert result["opposing_strategies"] == 1

    assert result["top_strategy"] == "trend_following"