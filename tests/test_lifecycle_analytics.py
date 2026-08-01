from intelligence.lifecycle.lifecycle_analytics import (
    LifecycleAnalytics
)

from intelligence.lifecycle.lifecycle_history import (
    LifecycleHistory
)

from intelligence.lifecycle.lifecycle_event import (
    LifecycleEvent
)



def test_lifecycle_analytics_active_strategy():

    history = LifecycleHistory()


    history.add(
        LifecycleEvent(

            strategy_name="trend_strategy_v2",

            from_state="CREATED",

            to_state="CANDIDATE",

            reason="strategy created"

        )
    )


    history.add(
        LifecycleEvent(

            strategy_name="trend_strategy_v2",

            from_state="CANDIDATE",

            to_state="ACTIVE",

            reason="governance approved"

        )
    )


    analytics = LifecycleAnalytics()


    result = analytics.analyze(
        "trend_strategy_v2",
        history
    )


    assert result.strategy_name == "trend_strategy_v2"

    assert result.total_events == 2

    assert result.transitions == 2

    assert result.current_state == "ACTIVE"

    assert result.lifecycle_score == 40

    assert result.health == "GOOD"



def test_lifecycle_analytics_champion_strategy():

    history = LifecycleHistory()


    history.add(
        LifecycleEvent(

            strategy_name="champion_strategy",

            from_state="ACTIVE",

            to_state="CHAMPION",

            reason="best performance"

        )
    )


    analytics = LifecycleAnalytics()


    result = analytics.analyze(
        "champion_strategy",
        history
    )


    assert result.current_state == "CHAMPION"

    assert result.health == "EXCELLENT"



def test_lifecycle_analytics_unknown_strategy():

    history = LifecycleHistory()


    analytics = LifecycleAnalytics()


    result = analytics.analyze(
        "unknown_strategy",
        history
    )


    assert result.strategy_name == "unknown_strategy"

    assert result.total_events == 0

    assert result.current_state == "UNKNOWN"

    assert result.lifecycle_score == 0

    assert result.health == "UNKNOWN"