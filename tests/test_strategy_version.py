from intelligence.learning.strategy_version import StrategyVersion


def test_strategy_version_creation():

    strategy = StrategyVersion(
        name="trend_following",
        score=75,
        success_rate=0.7
    )


    assert strategy.version == "v1"

    assert strategy.generation == 1

    assert strategy.status == "ACTIVE"



def test_strategy_evolution_creates_new_version():

    strategy = StrategyVersion(
        name="trend_following",
        score=75,
        success_rate=0.7
    )


    evolved = strategy.evolve(
        new_score=85,
        new_success_rate=0.8
    )


    assert evolved.version == "v2"

    assert evolved.generation == 2

    assert evolved.parent_strategy == "trend_following"

    assert evolved.status == "CANDIDATE"



def test_strategy_lifecycle():

    strategy = StrategyVersion(
        name="mean_reversion"
    )


    strategy.retire()

    assert strategy.status == "RETIRED"


    strategy.archive()

    assert strategy.status == "ARCHIVED"