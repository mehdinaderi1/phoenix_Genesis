from datetime import datetime, timezone

from intelligence.evolution.evolution_history import (
    EvolutionHistory,
    EvolutionRecord,
)

from intelligence.evolution.evolution_tree import (
    EvolutionTree,
)


def test_children_lookup():

    history = EvolutionHistory()

    history.add(
        EvolutionRecord(
            parent="trend_v1",
            child="trend_v2",
            generation=2,
            reason="performance",
            score_before=70,
            score_after=85,
            timestamp=datetime.now(timezone.utc),
        )
    )

    tree = EvolutionTree(history)

    assert tree.children_of("trend_v1") == [
        "trend_v2"
    ]



def test_lineage():

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


    assert tree.lineage(
        "trend_v3"
    ) == [
        "trend_v1",
        "trend_v2",
        "trend_v3"
    ]