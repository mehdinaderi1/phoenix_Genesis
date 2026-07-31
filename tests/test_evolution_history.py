from datetime import datetime, timezone

from intelligence.evolution.evolution_history import (
    EvolutionHistory,
    EvolutionRecord,
)


def test_store_history():

    history = EvolutionHistory()

    record = EvolutionRecord(
        parent="trend_v1",
        child="trend_v2",
        generation=2,
        reason="performance",
        score_before=72,
        score_after=88,
        timestamp=datetime.now(timezone.utc),
    )

    history.add(record)

    assert len(history.all()) == 1
    assert history.latest().child == "trend_v2"


def test_children_lookup():

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
            parent="A",
            child="C",
            generation=2,
            reason="alternative",
            score_before=70,
            score_after=78,
            timestamp=datetime.now(timezone.utc),
        )
    )

    assert len(history.children_of("A")) == 2