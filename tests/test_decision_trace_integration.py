from intelligence.decision_engine import DecisionEngine
from intelligence.report import MarketReport


def test_decision_result_contains_trace():

    engine = DecisionEngine()

    report = MarketReport(
        symbol="BTCUSDT",
        timeframe="30m",
        trend="UP",
        regime="TREND",
        signal="BUY",
        confidence=85,
        risk="LOW",
        reasons=[
            "strong momentum"
        ],
        strategy_consensus={
            "decision": "BUY",
            "supporting_strategies": 3,
            "opposing_strategies": 1,
            "confidence": 0.85,
            "top_strategy": "momentum_strategy"
        }
    )


    result = engine.decide(report)


    assert "trace" in result.metadata

    trace = result.metadata["trace"]


    assert trace["decision"] == result.action

    assert trace["signal"] == "BUY"

    assert trace["risk"] == "LOW"

    assert trace["gates"]["consensus"] is True

    assert trace["explanation"] is not None