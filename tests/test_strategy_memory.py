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