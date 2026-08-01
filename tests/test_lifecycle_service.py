from intelligence.lifecycle.lifecycle_service import (
    LifecycleService
)

from intelligence.lifecycle.lifecycle_history import (
    LifecycleHistory
)

from intelligence.lifecycle.lifecycle_event import (
    LifecycleEvent
)


def test_lifecycle_service_returns_metrics_and_decision():

    history = LifecycleHistory()


    history.add(
        LifecycleEvent(
            "service_strategy",
            None,
            "CANDIDATE",
            "candidate created"
        )
    )


    service = LifecycleService()


    result = service.evaluate(
        history
    )


    assert result["metrics"].strategy_name == "service_strategy"

    assert result["decision"].action == "EVALUATE"