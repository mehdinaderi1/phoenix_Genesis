from intelligence.decision_engine import DecisionEngine
from intelligence.report import MarketReport


def test_decision_engine_reports_both_long_and_short_checks(capsys):

    report = MarketReport(
        symbol="BTCUSDT",
        timeframe="30m",
        trend="DOWN",
        regime="TREND",
        signal="SELL",
        confidence=75,
        risk="HIGH",
        reasons=["bearish momentum"],
    )

    engine = DecisionEngine()

    result = engine.decide(report)

    captured = capsys.readouterr().out

    assert "CAN LONG:" in captured
    assert "LONG CHECK:" in captured
    assert "CAN SHORT:" in captured
    assert "SHORT CHECK:" in captured

    assert result.action == "PREPARE_SHORT"
