from intelligence.evolution.evolution_memory import (
    EvolutionMemory
)

from intelligence.evolution.evolution_history import (
    EvolutionRecord
)

from datetime import datetime, timezone



def record(
    parent,
    child,
    generation,
    score
):

    return EvolutionRecord(

        parent=parent,

        child=child,

        generation=generation,

        reason="performance",

        score_before=score - 10,

        score_after=score,

        timestamp=datetime.now(
            timezone.utc
        )
    )



def test_memory_store_and_count():

    memory = EvolutionMemory()


    memory.store(
        record(
            "trend_v1",
            "trend_v2",
            2,
            90
        )
    )


    assert memory.count() == 1



def test_memory_lineage_recall():

    memory = EvolutionMemory()


    memory.store(
        record(
            "trend_v1",
            "trend_v2",
            2,
            90
        )
    )


    memory.store(
        record(
            "trend_v2",
            "trend_v3",
            3,
            95
        )
    )


    lineage = memory.get_lineage(
        "trend_v3"
    )


    assert len(lineage) == 2

    assert lineage[-1].child == "trend_v3"



def test_memory_best_strategy():

    memory = EvolutionMemory()


    memory.store(
        record(
            "trend_v1",
            "trend_v2",
            2,
            85
        )
    )


    memory.store(
        record(
            "trend_v2",
            "trend_v3",
            3,
            95
        )
    )


    best = memory.best(
        "trend_v3"
    )


    assert best.score_after == 95