from intelligence.strategy_memory import StrategyMemory

from intelligence.learning.strategy_update import StrategyUpdate

from intelligence.strategy_evaluator import StrategyEvaluator

from intelligence.learning.strategy_optimizer import StrategyScore



def test_quality_strategy_saved():

    memory = StrategyMemory()

    evaluator = StrategyEvaluator()

    updater = StrategyUpdate(
        memory
    )


    strategy = StrategyScore(
        "Trend",
        85
    )


    evaluation = evaluator.evaluate({

        "samples": 10,

        "success_rate": 0.8,

        "score": strategy.score

    })


    assert evaluation["accepted"] is True


    if evaluation["accepted"]:

        updater.update(
            strategy
        )


    assert memory.count() == 1



def test_low_quality_strategy_rejected():

    memory = StrategyMemory()

    evaluator = StrategyEvaluator()


    evaluation = evaluator.evaluate({

        "samples": 1,

        "success_rate": 0.2,

        "score": 20

    })


    assert evaluation["accepted"] is False

    assert memory.count() == 0