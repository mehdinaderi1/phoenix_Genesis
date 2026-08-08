from intelligence.strategy_council import StrategyCouncil


def test_multi_strategy_council_consensus():

    strategies = [

        {
            "name": "trend_following",
            "action": "BUY",
            "confidence": 90
        },

        {
            "name": "breakout_strategy",
            "action": "BUY",
            "confidence": 80
        },

        {
            "name": "mean_reversion",
            "action": "WAIT",
            "confidence": 60
        }
    ]


    council = StrategyCouncil()


    result = council.evaluate(
        strategies
    )


    assert result is not None

    assert result["decision"] == "BUY"

    assert result["supporting_strategies"] == 2

    assert result["opposing_strategies"] == 1