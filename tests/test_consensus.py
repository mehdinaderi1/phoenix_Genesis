from intelligence.consensus import ConsensusResult


def test_consensus_result_creation():

    result = ConsensusResult(
        trend="BULLISH",
        signal="BUY",
        confidence=82
    )

    summary = result.summary()

    assert summary["trend"] == "BULLISH"
    assert summary["signal"] == "BUY"
    assert summary["confidence"] == 82