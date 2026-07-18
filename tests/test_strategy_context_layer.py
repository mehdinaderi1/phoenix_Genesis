from intelligence.strategy_memory import StrategyMemory
from intelligence.strategy_recall import StrategyRecall
from intelligence.strategy_context import StrategyContext


def test_strategy_context_layer():

    memory = StrategyMemory()


    memory.store({

        "strategy": "Trend_FOLLOW",

        "regime": "BULLISH",

        "signal": "BUY",

        "risk": "LOW",

        "score": 90

    })


    recall = StrategyRecall(
        memory
    )


    context = StrategyContext(
        recall
    )


    result = context.analyze(
        "BULLISH",
        "BUY",
        "LOW"
    )


    assert result is not None

    assert result["strategy"] == "Trend_FOLLOW"

    assert result["score"] == 90