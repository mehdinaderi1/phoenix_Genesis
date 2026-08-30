from intelligence.strategy_learner import StrategyLearner
from intelligence.strategy_memory import StrategyMemory


def test_strategy_learner_creates_multiple_strategies_from_one_pattern():

    memory = StrategyMemory()

    learner = StrategyLearner(
        strategy_memory=memory
    )

    patterns = [

        {
            "pattern": (
                "TREND",
                "BUY",
                "LOW"
            ),

            "strategy": "strategy_A",

            "samples": 10,

            "success_rate": 0.8,

            "avg_score": 80
        },

        {
            "pattern": (
                "TREND",
                "BUY",
                "LOW"
            ),

            "strategy": "strategy_B",

            "samples": 10,

            "success_rate": 0.7,

            "avg_score": 70
        }

    ]

    learned = learner.learn(
        patterns
    )

    assert len(learned) == 2

    assert memory.count() == 2

    strategy_names = {
        item["strategy"]
        for item in learned
    }

    assert strategy_names == {
        "strategy_A",
        "strategy_B"
    }

    strategy_A = next(
        item
        for item in learned
        if item["strategy"] == "strategy_A"
    )

    strategy_B = next(
        item
        for item in learned
        if item["strategy"] == "strategy_B"
    )

    assert strategy_A["regime"] == "TREND"
    assert strategy_A["signal"] == "BUY"
    assert strategy_A["risk"] == "LOW"

    assert strategy_A["samples"] == 10
    assert strategy_A["success_rate"] == 0.8
    assert strategy_A["score"] == 80

    assert strategy_B["regime"] == "TREND"
    assert strategy_B["signal"] == "BUY"
    assert strategy_B["risk"] == "LOW"

    assert strategy_B["samples"] == 10
    assert strategy_B["success_rate"] == 0.7
    assert strategy_B["score"] == 70
