from datetime import datetime, timezone


from intelligence.evolution.evolution_history import (
    EvolutionHistory,
    EvolutionRecord,
)

from intelligence.evolution.evolution_tree import (
    EvolutionTree,
)

from intelligence.evolution.strategy_lineage import (
    StrategyLineage,
)



def test_root_detection():

    history = EvolutionHistory()


    history.add(
        EvolutionRecord(
            parent="trend_v1",
            child="trend_v2",
            generation=2,
            reason="upgrade",
            score_before=70,
            score_after=80,
            timestamp=datetime.now(timezone.utc),
        )
    )


    history.add(
        EvolutionRecord(
            parent="trend_v2",
            child="trend_v3",
            generation=3,
            reason="optimization",
            score_before=80,
            score_after=90,
            timestamp=datetime.now(timezone.utc),
        )
    )


    tree = EvolutionTree(history)

    lineage = StrategyLineage(tree)


    assert lineage.root_of(
        "trend_v3"
    ) == "trend_v1"



def test_family_tree():

    history = EvolutionHistory()


    history.add(
        EvolutionRecord(
            parent="A",
            child="B",
            generation=2,
            reason="upgrade",
            score_before=70,
            score_after=80,
            timestamp=datetime.now(timezone.utc),
        )
    )


    history.add(
        EvolutionRecord(
            parent="B",
            child="C",
            generation=3,
            reason="upgrade",
            score_before=80,
            score_after=90,
            timestamp=datetime.now(timezone.utc),
        )
    )


    tree = EvolutionTree(history)

    lineage = StrategyLineage(tree)


    assert lineage.family(
        "C"
    ) == [
        "A",
        "B",
        "C"
    ]