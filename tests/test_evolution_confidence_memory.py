from intelligence.evolution.evolution_confidence_memory import (
    EvolutionConfidenceMemory
)



def test_confidence_memory_store():

    memory = EvolutionConfidenceMemory()


    memory.store(

        "momentum_strategy_v2",

        90

    )


    assert (
        memory.count()
        ==
        1
    )


    result = memory.latest(
        "momentum_strategy_v2"
    )


    assert result is not None


    assert (
        result["confidence"]
        ==
        90
    )



def test_confidence_memory_recall():

    memory = EvolutionConfidenceMemory()


    memory.store(
        "strategy_v2",
        85
    )

    memory.store(
        "strategy_v3",
        70
    )


    records = memory.recall(
        "strategy_v2"
    )


    assert len(records) == 1


    assert (
        records[0]["confidence"]
        ==
        85
    )



def test_average_confidence():

    memory = EvolutionConfidenceMemory()


    memory.store(
        "momentum_v2",
        80
    )


    memory.store(
        "momentum_v2",
        100
    )


    avg = memory.average_confidence(
        "momentum_v2"
    )


    assert avg == 90