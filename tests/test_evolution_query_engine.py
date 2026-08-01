from intelligence.lifecycle.evolution_memory_graph import (
    EvolutionMemoryGraph
)

from intelligence.lifecycle.evolution_query_engine import (
    EvolutionQueryEngine
)


def test_evolution_query_engine():

    memory = EvolutionMemoryGraph()


    memory.add_event(
        strategy="MomentumStrategy",
        generation=0,
        action="CREATE",
        performance_after=70
    )


    memory.add_event(
        strategy="MomentumStrategy_v2",
        parent_strategy="MomentumStrategy",
        generation=1,
        action="IMPROVE",
        performance_before=70,
        performance_after=82
    )


    memory.add_event(
        strategy="MomentumStrategy_v3",
        parent_strategy="MomentumStrategy_v2",
        generation=2,
        action="IMPROVE",
        performance_before=82,
        performance_after=91
    )


    query = EvolutionQueryEngine(
        memory
    )


    best = query.get_best_strategy()


    assert best["strategy"] == (
        "MomentumStrategy_v3"
    )


    assert query.get_generation(
        "MomentumStrategy_v3"
    ) == 2


    assert query.get_evolution_path(
        "MomentumStrategy_v3"
    ) == [
        "MomentumStrategy_v3",
        "MomentumStrategy_v2",
        "MomentumStrategy"
    ]