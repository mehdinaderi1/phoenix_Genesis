from intelligence.lifecycle.strategy_lifecycle_manager import (
    StrategyLifecycleManager
)

from intelligence.learning.strategy_version import (
    StrategyVersion
)


def test_strategy_lifecycle_full_flow():

    strategy = StrategyVersion(
        name="trend_strategy"
    )

    lifecycle = StrategyLifecycleManager()


    lifecycle.create(strategy)

    assert strategy.status == "CREATED"



    lifecycle.promote_candidate(strategy)

    assert strategy.status == "CANDIDATE"



    lifecycle.activate(strategy)

    assert strategy.status == "ACTIVE"



    lifecycle.promote_champion(strategy)

    assert strategy.status == "CHAMPION"



def test_strategy_lifecycle_retire():

    strategy = StrategyVersion(
        name="old_strategy"
    )

    lifecycle = StrategyLifecycleManager()


    lifecycle.retire(strategy)

    assert strategy.status == "RETIRED"



def test_strategy_lifecycle_archive():

    strategy = StrategyVersion(
        name="failed_strategy"
    )

    lifecycle = StrategyLifecycleManager()


    lifecycle.archive(strategy)

    assert strategy.status == "ARCHIVED"