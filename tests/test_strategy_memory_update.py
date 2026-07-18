from intelligence.strategy_memory import StrategyMemory



def test_strategy_memory_update_better_score():

    memory = StrategyMemory()


    memory.store({

        "strategy": "Trend",

        "score": 70

    })


    updated = memory.update_strategy({

        "strategy": "Trend",

        "score": 85

    })


    assert updated is True


    record = memory.latest()


    assert record["score"] == 85



def test_strategy_memory_reject_lower_score():

    memory = StrategyMemory()


    memory.store({

        "strategy": "Trend",

        "score": 80

    })


    updated = memory.update_strategy({

        "strategy": "Trend",

        "score": 60

    })


    assert updated is False


    record = memory.latest()


    assert record["score"] == 80