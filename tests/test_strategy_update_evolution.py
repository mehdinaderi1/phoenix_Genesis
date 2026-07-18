from intelligence.strategy_memory import StrategyMemory

from intelligence.learning.strategy_update import StrategyUpdate

from intelligence.learning.strategy_optimizer import StrategyScore



def test_strategy_update_evolves_existing_strategy():

    memory = StrategyMemory()


    updater = StrategyUpdate(
        memory
    )


    updater.update(
        StrategyScore(
            "Trend",
            70
        )
    )


    updater.update(
        StrategyScore(
            "Trend",
            85
        )
    )


    assert memory.count() == 1


    record = memory.latest()


    assert record["score"] == 85