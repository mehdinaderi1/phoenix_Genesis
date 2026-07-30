from intelligence.strategy_bridge import StrategyBridge
from intelligence.learning.strategy_version import StrategyVersion


def test_strategy_bridge_integration():

    strategy = StrategyVersion(
        name="momentum",
        score=90,
        success_rate=0.8
    )


    bridge = StrategyBridge()


    context = {

        "symbol": "BTCUSDT"

    }


    result = bridge.enrich_market_context(
        context,
        [strategy]
    )


    assert "champion_strategy" in result

    assert result["champion_strategy"]["name"] == "momentum"