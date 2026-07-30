from intelligence.learning.strategy_version import StrategyVersion
from intelligence.governance.strategy_governor import StrategyGovernor



def test_governor_approves_good_strategy():

    strategy = StrategyVersion(
        name="trend",
        score=85,
        success_rate=0.8
    )


    governor = StrategyGovernor()


    result = governor.evaluate(strategy)


    assert result == "APPROVED"

    assert strategy.status == "ACTIVE"



def test_governor_archives_bad_strategy():

    strategy = StrategyVersion(
        name="weak_strategy",
        score=30,
        success_rate=0.2
    )


    governor = StrategyGovernor()


    result = governor.evaluate(strategy)


    assert result == "ARCHIVED"

    assert strategy.status == "ARCHIVED"



def test_select_champion_strategy():

    s1 = StrategyVersion(
        name="strategy_a",
        score=80,
        success_rate=0.7
    )


    s2 = StrategyVersion(
        name="strategy_b",
        score=90,
        success_rate=0.5
    )


    governor = StrategyGovernor()


    champion = governor.select_champion(
        [
            s1,
            s2
        ]
    )


    assert champion.name == "strategy_a"