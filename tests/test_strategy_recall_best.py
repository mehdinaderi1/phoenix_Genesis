from intelligence.strategy_memory import StrategyMemory

from intelligence.strategy_recall import StrategyRecall



def test_strategy_recall_returns_best_strategy():

    memory = StrategyMemory()


    memory.store({

        "strategy": "Trend",

        "regime": "bullish",

        "signal": "buy",

        "risk": "low",

        "score": 70

    })


    memory.store({

        "strategy": "Trend",

        "regime": "bullish",

        "signal": "buy",

        "risk": "low",

        "score": 90

    })


    memory.store({

        "strategy": "Trend",

        "regime": "bullish",

        "signal": "buy",

        "risk": "low",

        "score": 80

    })


    recall = StrategyRecall(
        memory
    )


    result = recall.best(
        "bullish",
        "buy",
        "low"
    )


    assert result is not None

    assert result["score"] == 90