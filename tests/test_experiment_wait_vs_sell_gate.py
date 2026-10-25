from intelligence.decision_engine import DecisionEngine
from intelligence.report import MarketReport


def make_report(signal):
    return MarketReport(
        symbol="BTCUSDT",
        timeframe="Multi",
        trend="BEARISH",
        regime="TREND",
        signal=signal,
        confidence=75,
        risk="HIGH",
        reasons=["controlled WAIT vs SELL gate experiment"],
        operational_strategy_result={
            "strategy": "BTC_MTF_TREND_ALIGNMENT_V1",
            "signal": "SELL",
            "direction": "SHORT",
            "matched": True,
        },
    )


def test_wait_vs_sell_with_same_operational_short_signal():
    wait_decision = DecisionEngine().decide(make_report("WAIT"))
    sell_decision = DecisionEngine().decide(make_report("SELL"))

    print("CONTROLLED RESULT:", {
        "report_WAIT": wait_decision.action,
        "report_SELL": sell_decision.action,
    })

    assert wait_decision.action == "WAIT"
    assert sell_decision.action == "PREPARE_SHORT"
