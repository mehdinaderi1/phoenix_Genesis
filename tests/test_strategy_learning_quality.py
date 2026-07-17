from intelligence.strategy_memory import StrategyMemory
from intelligence.strategy_learner import StrategyLearner



def test_only_quality_strategies_are_saved():

    memory = StrategyMemory()


    learner = StrategyLearner(
        memory
    )


    patterns = [

        {
            "pattern": (
                "bullish",
                "buy",
                "low"
            ),

            "samples": 50,

            "success_rate": 0.8,

            "avg_score": 8

        },


        {
            "pattern": (
                "bearish",
                "sell",
                "high"
            ),

            "samples": 2,

            "success_rate": 0.9,

            "avg_score": 7

        }

    ]


    result = learner.learn(
        patterns
    )


    assert len(result) == 1

    assert memory.count() == 1

    assert (
        memory.latest()["strategy"]
        ==
        "bullish_buy_low"
    )