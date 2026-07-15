from intelligence.consensus import ConsensusResult
from intelligence.risk_analyzer import RiskAnalyzer
from intelligence.reasoning import ReasoningEngine


def test_reasoning_with_risk():

    consensus = ConsensusResult(
        trend="BULLISH",
        signal="BUY",
        confidence=85
    )

    risk = RiskAnalyzer().analyze(
        consensus
    )

    engine = ReasoningEngine()

    result = engine.generate(
        consensus,
        risk
    )

    assert result["risk"] == "LOW"
    assert "High confidence consensus" in result["reasons"]