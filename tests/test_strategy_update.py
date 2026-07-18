from intelligence.learning.strategy_update import StrategyUpdate
from intelligence.strategy_memory import StrategyMemory
from intelligence.learning.strategy_optimizer import StrategyScore



def test_strategy_update():

    memory = StrategyMemory()

    updater = StrategyUpdate(
        memory
    )


    score = StrategyScore(
        "Trend",
        75
    )


    result = updater.update(
        score
    )


    assert result["strategy"] == "Trend"

    assert result["score"] == 75

    assert memory.count() == 1