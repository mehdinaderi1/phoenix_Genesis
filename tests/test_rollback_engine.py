from datetime import datetime, timezone


from intelligence.evolution.evolution_history import (
    EvolutionHistory,
    EvolutionRecord,
)

from intelligence.evolution.rollback_engine import (
    RollbackEngine,
)



def test_previous_version():

    history = EvolutionHistory()


    history.add(
        EvolutionRecord(
            parent="trend_v1",
            child="trend_v2",
            generation=2,
            reason="upgrade",
            score_before=70,
            score_after=85,
            timestamp=datetime.now(timezone.utc),
        )
    )


    engine = RollbackEngine(
        history
    )


    assert engine.previous_version(
        "trend_v2"
    ) == "trend_v1"



def test_successful_rollback():

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


    engine = RollbackEngine(
        history
    )


    result = engine.rollback(
        "B"
    )


    assert result["rolled_back"] is True
    assert result["strategy"] == "A"



def test_failed_rollback():

    history = EvolutionHistory()


    engine = RollbackEngine(
        history
    )


    result = engine.rollback(
        "unknown"
    )


    assert result["rolled_back"] is False