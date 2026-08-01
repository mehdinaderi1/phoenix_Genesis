from intelligence.lifecycle.evolution_memory_graph import (
    EvolutionMemoryGraph
)


def test_evolution_memory_graph():

    memory = EvolutionMemoryGraph()


    memory.add_event(
        strategy="MomentumStrategy",
        generation=0,
        action="CREATE",
        reason="initial strategy",
        performance_before=None,
        performance_after=70
    )


    memory.add_event(
        strategy="MomentumStrategy_v2",
        parent_strategy="MomentumStrategy",
        generation=1,
        action="IMPROVE",
        reason="higher confidence",
        performance_before=70,
        performance_after=82
    )


    history = memory.find_strategy(
        "MomentumStrategy_v2"
    )


    assert len(history) == 1

    assert history[0]["parent_strategy"] == (
        "MomentumStrategy"
    )


    assert memory.get_lineage(
        "MomentumStrategy_v2"
    ) == [
        "MomentumStrategy_v2",
        "MomentumStrategy"
    ]