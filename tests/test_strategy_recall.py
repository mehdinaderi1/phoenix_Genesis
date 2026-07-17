from intelligence.strategy_memory import StrategyMemory
from intelligence.strategy_recall import StrategyRecall


def test_strategy_recall():

    memory = StrategyMemory()


    memory.store(
        {
            "strategy": "bullish_buy_low",
            "regime": "bullish",
            "signal": "buy",
            "risk": "low",
            "success_rate": 0.75
        }
    )


    recall = StrategyRecall(
        memory
    )


    result = recall.recall(
        "bullish",
        "buy",
        "low"
    )


    assert len(result) == 1

    assert result[0]["strategy"] == (
        "bullish_buy_low"
    )

    assert result[0]["success_rate"] == 0.75