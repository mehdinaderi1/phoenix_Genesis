from intelligence.evolution.evolution_memory import (
    EvolutionMemory
)

from intelligence.evolution.evolution_memory_intelligence import (
    EvolutionMemoryIntelligence
)

from intelligence.evolution.evolution_history import (
    EvolutionRecord
)

from datetime import datetime, timezone



def create_record(
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



def test_memory_intelligence_analysis():


    memory = EvolutionMemory()


    memory.store(

        create_record(

            "momentum_strategy",

            "momentum_strategy_v2",

            85

        )

    )


    intelligence = EvolutionMemoryIntelligence(
        memory
    )


    result = intelligence.analyze(
        "momentum_strategy_v2"
    )


    assert result["known"] is True

    assert result["evolution_count"] == 1

    assert result["best_score"] == 85



def test_memory_intelligence_unknown_strategy():


    memory = EvolutionMemory()


    intelligence = EvolutionMemoryIntelligence(
        memory
    )


    result = intelligence.analyze(
        "unknown"
    )


    assert result["known"] is False

    assert result["evolution_count"] == 0



def test_should_not_evolve_best_strategy():


    memory = EvolutionMemory()


    memory.store(

        create_record(

            "strategy",

            "strategy_v2",

            95

        )

    )


    intelligence = EvolutionMemoryIntelligence(
        memory
    )


    assert (
        intelligence.should_evolve(
            "strategy_v2"
        )
        is False
    )