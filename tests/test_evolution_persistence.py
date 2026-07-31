from datetime import datetime, timezone


from intelligence.learning.strategy_evolution_engine import (
    StrategyEvolutionEngine,
)

from intelligence.evolution.evolution_history import (
    EvolutionHistory,
    EvolutionRecord,
)



def test_evolution_result_saved_in_history():

    history = EvolutionHistory()

    engine = StrategyEvolutionEngine()


    strategy = {

        "name": "trend_v1",

        "score": 85,

        "success_rate": 0.8,

        "generation": 1

    }


    result = engine.evolve(
        strategy,
        strategy["score"]
    )


    record = EvolutionRecord(

        parent=result["parent"],

        child=result["strategy"],

        generation=result["generation"],

        reason="performance improvement",

        score_before=strategy["score"],

        score_after=result["score"],

        timestamp=datetime.now(timezone.utc)

    )


    history.add(record)


    latest = history.latest()


    assert latest.parent == "trend_v1"

    assert latest.child == "trend_v1_v2"

    assert latest.generation == 2

    assert latest.score_before == 85

    assert latest.score_after == 95



def test_lineage_lookup_after_evolution():

    history = EvolutionHistory()


    history.add(

        EvolutionRecord(

            parent="trend_v1",

            child="trend_v2",

            generation=2,

            reason="upgrade",

            score_before=80,

            score_after=90,

            timestamp=datetime.now(timezone.utc)

        )

    )


    children = history.children_of(
        "trend_v1"
    )


    assert len(children) == 1

    assert children[0].child == "trend_v2"