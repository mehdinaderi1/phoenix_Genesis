from intelligence.strategy_memory import StrategyMemory
from intelligence.strategy_recall import StrategyRecall


def test_strategy_context_returns_best_strategy():

    memory = StrategyMemory()


    memory.store({

        "strategy": "Trend_FOLLOW",

        "regime": "BULLISH",

        "signal": "BUY",

        "risk": "LOW",

        "score": 90

    })


    memory.store({

        "strategy": "Trend_SAFE",

        "regime": "BULLISH",

        "signal": "BUY",

        "risk": "LOW",

        "score": 70

    })


    recall = StrategyRecall(
        memory
    )


    context = recall.best(
        "BULLISH",
        "BUY",
        "LOW"
    )


    assert context is not None

    assert context["strategy"] == "Trend_FOLLOW"

    assert context["score"] == 90