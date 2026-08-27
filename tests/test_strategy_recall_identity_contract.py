from intelligence.strategy_memory import StrategyMemory
from intelligence.strategy_recall import StrategyRecall


def test_strategy_recall_preserves_learned_strategy_identity():

    memory = StrategyMemory()


    memory.store(
        {
            "strategy": "trend_following",

            "regime": "bullish",

            "signal": "buy",

            "risk": "low",

            "score": 85,

            "success_rate": 0.85,

            "samples": 20,

            "status": "ACTIVE"
        }
    )


    recall = StrategyRecall(
        memory
    )


    strategies = recall.recall(
        "BULLISH",
        "BUY",
        "LOW"
    )


    assert strategies


    champion = strategies[0]


    assert champion["strategy"] == (
        "trend_following"
    )



def test_best_strategy_returns_same_identity():

    memory = StrategyMemory()


    memory.store(
        {
            "strategy": "trend_following",

            "regime": "bullish",

            "signal": "buy",

            "risk": "low",

            "score": 85,

            "status": "ACTIVE"
        }
    )


    recall = StrategyRecall(
        memory
    )


    champion = recall.best(
        "bullish",
        "buy",
        "low"
    )


    assert champion is not None


    assert champion["strategy"] == (
        "trend_following"
    )