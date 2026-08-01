from intelligence.lifecycle.lifecycle_analytics import (
    LifecycleAnalytics
)

from intelligence.lifecycle.lifecycle_history import (
    LifecycleHistory
)

from intelligence.lifecycle.lifecycle_event import (
    LifecycleEvent
)


def test_lifecycle_analysis_available_in_report():


    history = LifecycleHistory()


    history.add(
        LifecycleEvent(

            strategy_name="trend_strategy",

            from_state="CANDIDATE",

            to_state="ACTIVE",

            reason="approved"

        )
    )


    analytics = LifecycleAnalytics()


    result = analytics.analyze(
        "trend_strategy",
        history
    )


    assert result.current_state == "ACTIVE"

    assert result.health == "GOOD"

    assert result.lifecycle_score == 20