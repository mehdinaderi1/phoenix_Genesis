from intelligence.lifecycle.lifecycle_event import (
    LifecycleEvent
)

from intelligence.lifecycle.lifecycle_history import (
    LifecycleHistory
)



def test_lifecycle_event_storage():

    history = LifecycleHistory()


    event = LifecycleEvent(

        strategy_name="trend_strategy",

        from_state="CREATED",

        to_state="CANDIDATE",

        reason="passed initial evaluation"

    )


    history.add(event)


    events = history.get_all()


    assert len(events) == 1

    assert events[0].strategy_name == "trend_strategy"

    assert events[0].from_state == "CREATED"

    assert events[0].to_state == "CANDIDATE"

    assert events[0].reason == "passed initial evaluation"



def test_lifecycle_latest_event():

    history = LifecycleHistory()


    first_event = LifecycleEvent(

        strategy_name="trend_strategy",

        from_state="CREATED",

        to_state="CANDIDATE",

        reason="candidate created"

    )


    second_event = LifecycleEvent(

        strategy_name="trend_strategy",

        from_state="CANDIDATE",

        to_state="ACTIVE",

        reason="quality gate passed"

    )


    history.add(first_event)

    history.add(second_event)


    latest = history.latest()


    assert latest.to_state == "ACTIVE"

    assert latest.reason == "quality gate passed"



def test_lifecycle_event_to_dict():

    event = LifecycleEvent(

        strategy_name="trend_strategy",

        from_state="ACTIVE",

        to_state="CHAMPION",

        reason="best performing strategy"

    )


    data = event.to_dict()


    assert data["strategy_name"] == "trend_strategy"

    assert data["from_state"] == "ACTIVE"

    assert data["to_state"] == "CHAMPION"

    assert data["reason"] == "best performing strategy"

    assert "created_at" in data