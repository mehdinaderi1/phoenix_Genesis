from intelligence.strategy_memory import StrategyMemory
from intelligence.strategy_score import StrategyScore
from intelligence.learning.strategy_update import StrategyUpdate
from intelligence.learning.strategy_history import StrategyHistory



def test_strategy_update_creates_history():

    memory = StrategyMemory()

    history = StrategyHistory()


    updater = StrategyUpdate(
        memory,
        strategy_history=history
    )


    score = StrategyScore(
        "Trend",
        80
    )


    updater.update(
        score
    )


    records = history.get_history(
        "Trend"
    )


    assert len(records) == 1

    assert records[0]["score"] == 80