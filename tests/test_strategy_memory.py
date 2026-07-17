from intelligence.strategy_memory import StrategyMemory


def test_strategy_memory():

    memory = StrategyMemory()

    record = {

        "strategy": "PREPARE_LONG",

        "score": 90

    }

    memory.store(record)

    assert memory.count() == 1

    latest = memory.latest()

    assert latest["strategy"] == "PREPARE_LONG"

    assert latest["score"] == 90



def test_strategy_memory_pattern_search():

    memory = StrategyMemory()


    memory.store(
        {
            "strategy": "PREPARE_LONG",
            "regime": "bullish",
            "signal": "buy",
            "risk": "low",
            "success_rate": 0.75
        }
    )


    results = memory.find_by_pattern(
        "bullish",
        "buy",
        "low"
    )


    assert len(results) == 1

    assert results[0]["success_rate"] == 0.75