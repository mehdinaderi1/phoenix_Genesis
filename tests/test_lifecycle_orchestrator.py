from intelligence.lifecycle.lifecycle_orchestrator import (
    LifecycleOrchestrator
)

from intelligence.lifecycle.lifecycle_history import (
    LifecycleHistory
)

from intelligence.lifecycle.lifecycle_event import (
    LifecycleEvent
)


def test_orchestrator_returns_keep_for_champion():

    history = LifecycleHistory()


    history.add(
        LifecycleEvent(
            "champion_strategy",
            "ACTIVE",
            "CHAMPION",
            "promoted to champion"
        )
    )


    orchestrator = LifecycleOrchestrator()


    result = orchestrator.run(
        history
    )


    assert result["decision"].action == "KEEP"

    assert result["metrics"].current_state == "CHAMPION"



def test_orchestrator_returns_improve_for_active():

    history = LifecycleHistory()


    history.add(
        LifecycleEvent(
            "active_strategy",
            "CANDIDATE",
            "ACTIVE",
            "activated"
        )
    )


    orchestrator = LifecycleOrchestrator()


    result = orchestrator.run(
        history
    )


    assert result["decision"].action == "IMPROVE"

    assert result["metrics"].current_state == "ACTIVE"



def test_orchestrator_returns_archive_for_retired():

    history = LifecycleHistory()


    history.add(
        LifecycleEvent(
            "old_strategy",
            "ACTIVE",
            "RETIRED",
            "retired"
        )
    )


    orchestrator = LifecycleOrchestrator()


    result = orchestrator.run(
        history
    )


    assert result["decision"].action == "ARCHIVE"



def test_orchestrator_returns_evaluate_for_candidate():

    history = LifecycleHistory()


    history.add(
        LifecycleEvent(
            "new_strategy",
            "UNKNOWN",
            "CANDIDATE",
            "created"
        )
    )


    orchestrator = LifecycleOrchestrator()


    result = orchestrator.run(
        history
    )


    assert result["decision"].action == "EVALUATE"