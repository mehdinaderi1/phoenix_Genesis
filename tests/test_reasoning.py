from intelligence.consensus import ConsensusResult
from intelligence.reasoning import ReasoningEngine


def test_reasoning_engine():

    consensus = ConsensusResult(
        trend="BULLISH",
        signal="BUY",
        confidence=85
    )

    engine = ReasoningEngine()

    result = engine.generate(consensus)

    assert result["signal"] == "BUY"
    assert result["risk"] == "LOW"
    assert "High confidence score" in result["reasons"]