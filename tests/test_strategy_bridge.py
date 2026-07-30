from intelligence.learning.strategy_version import StrategyVersion
from intelligence.strategy_bridge import StrategyBridge



def test_bridge_returns_champion_strategy():

    strategy_a = StrategyVersion(
        name="trend",
        score=90,
        success_rate=0.8
    )


    strategy_b = StrategyVersion(
        name="weak",
        score=40,
        success_rate=0.3
    )


    bridge = StrategyBridge()


    result = bridge.get_best_strategy(
        [
            strategy_a,
            strategy_b
        ]
    )


    assert result["name"] == "trend"

    assert result["status"] == "ACTIVE"



def test_bridge_enriches_market_context():

    strategy = StrategyVersion(
        name="breakout",
        score=85,
        success_rate=0.75
    )


    context = {

        "market": "BTCUSDT"

    }


    bridge = StrategyBridge()


    result = bridge.enrich_market_context(
        context,
        [strategy]
    )


    assert "champion_strategy" in result

    assert result["champion_strategy"]["name"] == "breakout"



def test_bridge_without_strategy():

    bridge = StrategyBridge()


    context = {

        "market": "BTCUSDT"

    }


    result = bridge.enrich_market_context(
        context,
        []
    )


    assert "champion_strategy" not in result