from intelligence.decision_engine import DecisionEngine


class MockReport:
    def __init__(self, signal, risk, confidence, operational_strategy_result=None):
        self.signal = signal
        self.risk = risk
        self.confidence = confidence
        self.operational_strategy_result = operational_strategy_result


def test_operational_strategy_buy_allows_long_path():
    report = MockReport(
        signal="BUY",
        risk="LOW",
        confidence=90,
        operational_strategy_result={
            "strategy": "BTC_MTF_TREND_ALIGNMENT_V1",
            "signal": "BUY",
            "direction": "LONG",
            "matched": True,
        }
    )

    decision = DecisionEngine().decide(report)

    assert decision.action == "PREPARE_LONG"


def test_operational_strategy_sell_allows_short_path():
    report = MockReport(
        signal="SELL",
        risk="LOW",
        confidence=90,
        operational_strategy_result={
            "strategy": "BTC_MTF_TREND_ALIGNMENT_V1",
            "signal": "SELL",
            "direction": "SHORT",
            "matched": True,
        }
    )

    decision = DecisionEngine().decide(report)

    assert decision.action == "PREPARE_SHORT"


def test_operational_strategy_wait_blocks_trading_path():
    report = MockReport(
        signal="BUY",
        risk="LOW",
        confidence=90,
        operational_strategy_result={
            "strategy": "BTC_MTF_TREND_ALIGNMENT_V1",
            "signal": "WAIT",
            "direction": None,
            "matched": False,
        }
    )

    decision = DecisionEngine().decide(report)

    assert decision.action == "WAIT"


def test_missing_operational_strategy_preserves_existing_behavior():
    report = MockReport(
        signal="BUY",
        risk="LOW",
        confidence=90
    )

    decision = DecisionEngine().decide(report)

    assert decision.action == "PREPARE_LONG"
