from intelligence.learning.strategy_ranker import (
    StrategyRanker
)



def test_strategy_ranking_orders_strategies():

    ranker = StrategyRanker()


    strategies = [

        {
            "strategy": "Breakout",
            "score": 70
        },

        {
            "strategy": "Trend",
            "score": 90
        },

        {
            "strategy": "Reversal",
            "score": 80
        }

    ]


    ranked = ranker.rank(
        strategies
    )


    assert ranked[0]["strategy"] == "Trend"

    assert ranked[1]["strategy"] == "Reversal"

    assert ranked[2]["strategy"] == "Breakout"



def test_best_strategy_selection():

    ranker = StrategyRanker()


    strategies = [

        {
            "strategy": "Trend",
            "score": 90
        },

        {
            "strategy": "Breakout",
            "score": 75
        }

    ]


    best = ranker.best(
        strategies
    )


    assert best["strategy"] == "Trend"