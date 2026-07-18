from intelligence.strategy_memory import StrategyMemory
from intelligence.learning.strategy_update import StrategyUpdate
from intelligence.learning.strategy_improvement_engine import (
    StrategyImprovementEngine
)
from intelligence.strategy_feedback import StrategyFeedback



def test_strategy_self_improvement_flow():

    memory = StrategyMemory()


    updater = StrategyUpdate(
        memory
    )


    improvement = StrategyImprovementEngine()


    feedback_layer = StrategyFeedback()


    # initial learned strategy

    updater.update(
        type(
            "StrategyScore",
            (),
            {
                "strategy": "Trend",
                "score": 70,
                "samples": 1,
                "success_rate": 1
            }
        )()
    )


    feedback = {

        "result": "SUCCESS",

        "score": 100

    }


    record = feedback_layer.create_record(
        "Trend",
        feedback
    )


    improved = improvement.improve(
        "Trend",
        70,
        [
            record
        ]
    )


    updater.update(
        improved
    )


    latest = memory.latest()


    assert latest["strategy"] == "Trend"

    assert latest["score"] == 75