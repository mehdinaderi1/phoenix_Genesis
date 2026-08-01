from intelligence.lifecycle.lifecycle_adapter import (
    LifecycleAdapter
)

from intelligence.lifecycle.strategy_lifecycle_manager import (
    StrategyLifecycleManager
)

from intelligence.lifecycle.lifecycle_history import (
    LifecycleHistory
)

from intelligence.learning.strategy_version import (
    StrategyVersion
)



def test_evolved_strategy_enters_lifecycle():

    strategy = StrategyVersion(
        name="trend_strategy_v2"
    )


    history = LifecycleHistory()


    manager = StrategyLifecycleManager(
        history
    )


    adapter = LifecycleAdapter(
        manager
    )


    adapter.register_evolved_strategy(
        strategy
    )


    assert strategy.status == "CANDIDATE"


    events = history.get_all()


    assert len(events) == 2


    assert events[0].to_state == "CREATED"

    assert events[1].to_state == "CANDIDATE"



def test_evolved_strategy_activation():

    strategy = StrategyVersion(
        name="momentum_strategy_v2"
    )


    history = LifecycleHistory()


    manager = StrategyLifecycleManager(
        history
    )


    adapter = LifecycleAdapter(
        manager
    )


    adapter.register_evolved_strategy(
        strategy
    )


    adapter.activate_evolved_strategy(
        strategy
    )


    assert strategy.status == "ACTIVE"


    latest = history.latest()


    assert latest.to_state == "ACTIVE"