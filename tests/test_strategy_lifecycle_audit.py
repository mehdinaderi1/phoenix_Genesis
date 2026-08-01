from intelligence.lifecycle.strategy_lifecycle_manager import (
    StrategyLifecycleManager
)

from intelligence.lifecycle.lifecycle_history import (
    LifecycleHistory
)

from intelligence.learning.strategy_version import (
    StrategyVersion
)


def test_strategy_activation_creates_audit_event():

    strategy = StrategyVersion(
        name="trend_strategy"
    )

    history = LifecycleHistory()

    lifecycle = StrategyLifecycleManager(
        history
    )


    lifecycle.create(strategy)

    lifecycle.promote_candidate(strategy)

    lifecycle.activate(strategy)


    assert strategy.status == "ACTIVE"


    events = history.get_all()


    assert len(events) == 3


    assert events[0].from_state == "ACTIVE" or events[0].from_state == "NEW"

    assert events[0].to_state == "CREATED"


    assert events[2].from_state == "CANDIDATE"

    assert events[2].to_state == "ACTIVE"



def test_strategy_retirement_creates_event():

    strategy = StrategyVersion(
        name="old_strategy"
    )

    history = LifecycleHistory()

    lifecycle = StrategyLifecycleManager(
        history
    )


    lifecycle.retire(strategy)


    assert strategy.status == "RETIRED"


    latest = history.latest()


    assert latest.to_state == "RETIRED"

    assert latest.strategy_name == "old_strategy"



def test_strategy_archive_creates_event():

    strategy = StrategyVersion(
        name="failed_strategy"
    )

    history = LifecycleHistory()

    lifecycle = StrategyLifecycleManager(
        history
    )


    lifecycle.archive(strategy)


    latest = history.latest()


    assert latest.from_state == "ACTIVE"

    assert latest.to_state == "ARCHIVED"

    assert latest.reason == "strategy archived"