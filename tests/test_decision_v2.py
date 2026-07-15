from intelligence.decision_engine import DecisionEngine
from intelligence.report import MarketReport


def test_decision_engine_v2():


    report = MarketReport(
        symbol="BTCUSDT",
        timeframe="Multi",
        trend="BULLISH",
        regime="TRENDING",
        signal="BUY",
        confidence=85,
        risk="LOW",
        reasons=[
            "Bullish trend confirmed"
        ]
    )


    engine = DecisionEngine()


    result = engine.decide(report)


    assert result.action == "PREPARE_LONG"

    assert result.confidence == 85

    assert "Strong bullish" in result.reason