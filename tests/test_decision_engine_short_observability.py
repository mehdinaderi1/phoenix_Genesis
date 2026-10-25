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

def test_decision_engine_reports_directional_gate_details(capsys):
    report = MarketReport(
        symbol="BTCUSDT",
        timeframe="30m",
        trend="DOWN",
        regime="TREND",
        signal="SELL",
        confidence=75,
        risk="HIGH",
        reasons=["bearish momentum"],
        operational_strategy_result={
            "strategy": "BTC_MTF_TREND_ALIGNMENT_V1",
            "signal": "SELL",
            "direction": "SHORT",
            "matched": True,
        },
    )

    result = DecisionEngine().decide(report)
    captured = capsys.readouterr().out

    assert result.action == "PREPARE_SHORT"
    assert "'operational_strategy_matched': True" in captured
    assert "'operational_strategy_signal': 'SELL'" in captured
    assert "'signal_is_sell': True" in captured
    assert "'confidence_at_least_70': True" in captured
    assert "'signal_is_buy': False" in captured
    assert "'confidence_at_least_80': False" in captured
    assert "'risk_is_low': False" in captured


def test_decision_engine_returns_wait_when_operational_strategy_does_not_match():
    report = MarketReport(
        symbol="BTCUSDT",
        timeframe="30m",
        trend="DOWN",
        regime="TREND",
        signal="SELL",
        confidence=75,
        risk="HIGH",
        reasons=["bearish momentum"],
        operational_strategy_result={
            "strategy": "BTC_MTF_TREND_ALIGNMENT_V1",
            "signal": "SELL",
            "direction": "SHORT",
            "matched": False,
        },
    )

    result = DecisionEngine().decide(report)

    assert result.action == "WAIT"
