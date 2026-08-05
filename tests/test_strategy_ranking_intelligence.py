from intelligence.learning.strategy_ranker import StrategyRanker


def test_strategy_ranker_considers_performance_quality():

    ranker = StrategyRanker()

    strategies = [

        {
            "strategy": "high_score_bad_history",
            "score": 95,
            "success_rate": 30,
            "samples": 5
        },

        {
            "strategy": "stable_strategy",
            "score": 85,
            "success_rate": 90,
            "samples": 100
        }

    ]


    ranked = ranker.rank(
        strategies
    )


    assert ranked[0]["strategy"] == "stable_strategy"



def test_strategy_ranker_handles_missing_metrics():

    ranker = StrategyRanker()

    strategies = [

        {
            "strategy": "simple_strategy",
            "score": 80
        },

        {
            "strategy": "better_strategy",
            "score": 90
        }

    ]


    ranked = ranker.rank(
        strategies
    )


    assert ranked[0]["strategy"] == "better_strategy"



def test_strategy_ranker_best_returns_champion():

    ranker = StrategyRanker()

    strategies = [

        {
            "strategy": "A",
            "score": 70,
            "success_rate": 60,
            "samples": 50
        },

        {
            "strategy": "B",
            "score": 85,
            "success_rate": 80,
            "samples": 100
        }

    ]


    best = ranker.best(
        strategies
    )


    assert best["strategy"] == "B"