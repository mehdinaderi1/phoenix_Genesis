from intelligence.strategy_ranking_builder import StrategyRankingBuilder
from intelligence.strategy_ranking_result import StrategyRankingResult


def test_strategy_ranking_result_builds_explainable_artifact():

    strategies = [

        {
            "strategy": "BTC_trend_lowrisk",
            "score": 91,
            "success_rate": 85,
            "samples": 100,
            "status": "ACTIVE",
        },

        {
            "strategy": "BTC_breakout",
            "score": 80,
            "success_rate": 70,
            "samples": 60,
            "status": "ACTIVE",
        }

    ]


    builder = StrategyRankingBuilder()


    result = builder.build(
        strategies,
        market_context={
            "regime": "TREND"
        }
    )


    assert isinstance(
        result,
        StrategyRankingResult
    )


    assert len(
        result.ranked_strategies
    ) == 2


    assert result.top_strategy is not None


    assert (
        result.top_strategy.rank
        == 1
    )


    assert (
        result.top_strategy.strategy_name
        == "BTC_trend_lowrisk"
    )


    assert (
        result.ranking_explanation
        is not None
    )


    assert (
        result.market_context["regime"]
        == "TREND"
    )