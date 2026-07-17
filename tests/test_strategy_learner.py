from intelligence.strategy_memory import StrategyMemory
from intelligence.strategy_learner import StrategyLearner


def test_strategy_learning():

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

            "avg_score": 7.5
        }

    ]


    result = learner.learn(
        patterns
    )


    assert len(result) == 1

    assert memory.count() == 1


    strategy = memory.latest()


    assert strategy["strategy"] == (
        "bullish_buy_low"
    )

    assert strategy["success_rate"] == 0.8