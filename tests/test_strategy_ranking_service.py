from intelligence.learning.strategy_ranker import StrategyRanker
from intelligence.strategy_ranking_service import StrategyRankingService
from intelligence.strategy_ranking_result import StrategyRankingResult


def test_strategy_ranking_service_returns_ranking_result():

    strategies = [

        {
            "strategy": "BTC_trend",
            "score": 90,
            "success_rate": 80,
            "samples": 100,
            "status": "ACTIVE",
        },

        {
            "strategy": "BTC_breakout",
            "score": 70,
            "success_rate": 60,
            "samples": 50,
            "status": "ACTIVE",
        }

    ]


    service = StrategyRankingService(
        StrategyRanker()
    )


    result = service.rank(
        strategies
    )


    assert isinstance(
        result,
        StrategyRankingResult
    )


    assert len(
        result.ranked_strategies
    ) == 2


    assert (
        result.top_strategy.strategy_name
        == "BTC_trend"
    )


    assert (
        result.top_strategy.rank
        == 1
    )