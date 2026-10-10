from intelligence.decision_engine import DecisionEngine
from intelligence.report import MarketReport
from intelligence.observation.opportunity_observer import OpportunityObserver


def make_report(**overrides):
    values = {
        "symbol": "BTCUSDT",
        "timeframe": "5m",
        "trend": "UP",
        "regime": "TREND",
        "signal": "BUY",
        "confidence": 85,
        "risk": "LOW",
        "reasons": ["strong momentum"],
        "strategy_consensus": {
            "decision": "BUY",
            "supporting_strategies": 3,
            "opposing_strategies": 1,
            "confidence": 0.85,
            "top_strategy": "momentum_strategy",
        },
        "operational_strategy_result": {
            "strategy": "TEST_STRATEGY",
            "signal": "BUY",
            "direction": "LONG",
            "matched": True,
        },
    }
    values.update(overrides)
    return MarketReport(**values)


def observe_with_existing_decision(report):
    decision = DecisionEngine().decide(report)
    return OpportunityObserver().observe(report, decision=decision), decision


def test_observer_records_buy_opportunity_without_executing_orders():
    report = make_report()

    opportunity, decision = observe_with_existing_decision(report)

    assert opportunity["symbol"] == "BTCUSDT"
    assert opportunity["signal"] == "BUY"
    assert opportunity["decision"] == decision.action == "PREPARE_LONG"
    assert opportunity["filters"]["signal"]["passed"] is True
    assert opportunity["filters"]["risk"]["passed"] is True
    assert opportunity["execution_attempted"] is False


def test_observer_records_blocked_opportunity_and_reasons():
    report = make_report(signal="BUY", risk="HIGH", confidence=55)

    opportunity, decision = observe_with_existing_decision(report)

    assert opportunity["signal"] == "BUY"
    assert opportunity["filters"]["risk"]["passed"] is False
    assert opportunity["filters"]["confidence"]["passed"] is False
    assert opportunity["decision"] == decision.action == "WAIT"
    assert opportunity["blocked_reasons"]
    assert opportunity["execution_attempted"] is False


def test_observer_does_not_mutate_report():
    report = make_report()
    original = report.summary().copy()

    observe_with_existing_decision(report)

    assert report.summary() == original

def test_observer_preserves_observation_timestamp():
    report = make_report()
    decision = DecisionEngine().decide(report)
    timestamp = "2026-10-10T00:00:00+00:00"

    opportunity = OpportunityObserver().observe(
        report,
        decision=decision,
        observation_timestamp=timestamp,
    )

    assert opportunity["observation_timestamp"] == timestamp
