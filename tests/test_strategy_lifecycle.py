from intelligence.learning.strategy_version import StrategyVersion
from intelligence.governance.strategy_lifecycle import StrategyLifecycle



def test_strategy_full_lifecycle():

    strategy = StrategyVersion(
        name="trend_strategy"
    )


    lifecycle = StrategyLifecycle()


    lifecycle.create(strategy)

    assert strategy.status == "CREATED"



    lifecycle.promote_candidate(strategy)

    assert strategy.status == "CANDIDATE"



    lifecycle.activate(strategy)

    assert strategy.status == "ACTIVE"



    lifecycle.promote_champion(strategy)

    assert strategy.status == "CHAMPION"



def test_strategy_retirement():

    strategy = StrategyVersion(
        name="old_strategy"
    )


    lifecycle = StrategyLifecycle()


    lifecycle.retire(strategy)


    assert strategy.status == "RETIRED"



def test_strategy_archive():

    strategy = StrategyVersion(
        name="failed_strategy"
    )


    lifecycle = StrategyLifecycle()


    lifecycle.archive(strategy)


    assert strategy.status == "ARCHIVED"