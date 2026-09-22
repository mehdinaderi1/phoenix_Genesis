from intelligence.consensus import ConsensusResult


def test_consensus_result_accepts_optional_breakdown():
    breakdown = {
        "timeframes": [],
        "weighted_confidence": 63.75,
        "signal_conflict": True,
        "conflict_penalty": 0.5
    }

    result = ConsensusResult(
        trend="BULLISH",
        signal="WAIT",
        confidence=31.875,
        breakdown=breakdown
    )

    assert result.trend == "BULLISH"
    assert result.signal == "WAIT"
    assert result.confidence == 31.875
    assert result.breakdown == breakdown


def test_consensus_result_breakdown_is_optional():
    result = ConsensusResult(
        trend="BULLISH",
        signal="BUY",
        confidence=70
    )

    assert result.breakdown is None
