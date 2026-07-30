from intelligence.governance.strategy_adapter import StrategyAdapter
from intelligence.learning.strategy_version import StrategyVersion



def test_convert_dict_strategy():

    strategy = {

        "name": "trend",

        "score": 85,

        "success_rate": 0.8

    }


    adapter = StrategyAdapter()


    result = adapter.convert(
        strategy
    )


    assert isinstance(
        result,
        StrategyVersion
    )


    assert result.name == "trend"

    assert result.score == 85



def test_convert_existing_version():

    strategy = StrategyVersion(

        name="breakout",

        score=90,

        success_rate=0.85

    )


    adapter = StrategyAdapter()


    result = adapter.convert(
        strategy
    )


    assert result is strategy



def test_convert_none():

    adapter = StrategyAdapter()


    result = adapter.convert(
        None
    )


    assert result is None