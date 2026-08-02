from intelligence.evolution.evolution_memory import (
    EvolutionMemory
)

from intelligence.evolution.evolution_memory_intelligence import (
    EvolutionMemoryIntelligence
)

from intelligence.evolution.evolution_self_awareness import (
    EvolutionSelfAwareness
)

from intelligence.evolution.evolution_history import (
    EvolutionRecord
)

from datetime import datetime, timezone



def record(
    parent,
    child,
    score
):

    return EvolutionRecord(

        parent=parent,

        child=child,

        generation=2,

        reason="test",

        score_before=50,

        score_after=score,

        timestamp=datetime.now(
            timezone.utc
        )

    )



def test_self_awareness_advanced_strategy():


    memory = EvolutionMemory()


    memory.store(

        record(

            "strategy",

            "strategy_v2",

            95

        )

    )


    intelligence = EvolutionMemoryIntelligence(
        memory
    )


    awareness = EvolutionSelfAwareness(
        intelligence
    )


    result = awareness.evaluate(
        "strategy_v2"
    )


    assert (
        result["maturity"]
        ==
        "ADVANCED"
    )


    assert (
        result["trend"]
        ==
        "IMPROVING"
    )


    assert (
        result["health"]
        ==
        0.95
    )



def test_self_awareness_new_strategy():


    memory = EvolutionMemory()


    intelligence = EvolutionMemoryIntelligence(
        memory
    )


    awareness = EvolutionSelfAwareness(
        intelligence
    )


    result = awareness.evaluate(
        "new_strategy"
    )


    assert (
        result["maturity"]
        ==
        "NEW"
    )


    assert (
        result["generation"]
        ==
        0
    )