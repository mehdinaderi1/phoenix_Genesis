from intelligence.learning.strategy_ranker import StrategyRanker
from intelligence.strategy_ranking_result import StrategyRankingResult


def test_strategy_ranker_returns_explainable_ranking_result():

    ranker = StrategyRanker()


    result = ranker.rank_with_result(
        [
            {
                "strategy": "BTC_trend_lowrisk",
                "score": 91,
                "success_rate": 85,
                "samples": 100,
                "status": "ACTIVE"
            },
            {
                "strategy": "BTC_breakout",
                "score": 80,
                "success_rate": 70,
                "samples": 60,
                "status": "ACTIVE"
            }
        ],
        market_context={
            "regime": "TREND"
        }
    )


    assert isinstance(
        result,
        StrategyRankingResult
    )


    assert result.top_strategy is not None


    assert (
        result.top_strategy.strategy_name
        ==
        "BTC_trend_lowrisk"
    )


    assert (
        result.top_strategy.rank
        ==
        1
    )


    assert (
        len(result.top_strategy.reasons)
        >
        0
    )