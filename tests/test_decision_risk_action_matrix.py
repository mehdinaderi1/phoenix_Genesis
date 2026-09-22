from intelligence.consensus import ConsensusResult
from intelligence.decision_engine import DecisionEngine
from intelligence.report import MarketReport
from intelligence.risk_analyzer import RiskAnalyzer


def build_report(signal, consensus_confidence, decision_confidence):
    consensus = ConsensusResult(
        trend="BULLISH" if signal == "BUY" else "BEARISH",
        signal=signal,
        confidence=consensus_confidence,
    )

    risk = RiskAnalyzer().analyze(consensus)

    report = MarketReport(
        symbol="BTCUSDT",
        timeframe="Multi",
        trend=consensus.trend,
        regime="TRENDING",
        signal=signal,
        confidence=decision_confidence,
        risk=risk.level,
        reasons=[f"Risk Level: {risk.level}"],
    )

    return report, risk


def test_risk_levels_follow_consensus_confidence():
    _, high = build_report("BUY", 40, 85)
    _, medium = build_report("BUY", 65, 85)
    _, low = build_report("BUY", 85, 85)

    assert high.level == "HIGH"
    assert medium.level == "MEDIUM"
    assert low.level == "LOW"


def test_risk_and_decision_action_matrix():
    engine = DecisionEngine()

    report, risk = build_report("BUY", 40, 85)
    result = engine.decide(report)
    assert risk.level == "HIGH"
    assert result.action == "WAIT"

    report, risk = build_report("SELL", 65, 75)
    result = engine.decide(report)
    assert risk.level == "MEDIUM"
    assert result.action == "PREPARE_SHORT"

    report, risk = build_report("BUY", 85, 85)
    result = engine.decide(report)
    assert risk.level == "LOW"
    assert result.action == "PREPARE_LONG"

    report, risk = build_report("SELL", 85, 85)
    result = engine.decide(report)
    assert risk.level == "LOW"
    assert result.action == "PREPARE_SHORT"


def test_decision_validator_rejects_wait_action():
    report, risk = build_report("WAIT", 40, 85)
    result = DecisionEngine().decide(report)

    assert risk.level == "HIGH"
    assert result.action == "WAIT"
