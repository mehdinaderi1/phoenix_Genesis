from intelligence.governance.strategy_adapter import StrategyAdapter
from intelligence.learning.strategy_version import StrategyVersion


def test_strategy_adapter_preserves_status():

    strategy = {
        "name": "old_strategy",
        "score": 95,
        "success_rate": 0.90,
        "status": "RETIRED",
        "version": "v3",
        "generation": 3,
        "parent_strategy": "old_parent"
    }


    adapter = StrategyAdapter()


    result = adapter.convert(
        strategy
    )


    assert isinstance(
        result,
        StrategyVersion
    )


    assert result.name == "old_strategy"

    assert result.score == 95

    assert result.success_rate == 0.90

    assert result.status == "RETIRED"

    assert result.version == "v3"

    assert result.generation == 3

    assert result.parent_strategy == "old_parent"