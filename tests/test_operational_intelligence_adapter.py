from intelligence.consensus import ConsensusResult

from core.market_data.operational_intelligence_adapter import (
    OperationalIntelligenceAdapter
)
from core.market_data.operational_intelligence_context import (
    OperationalIntelligenceContext
)


def test_operational_intelligence_adapter_creates_consensus():
    context = OperationalIntelligenceContext(
        symbol="BTCUSDT",
        trend="BULLISH",
        signal="BUY",
        confidence=85.0
    )

    consensus = OperationalIntelligenceAdapter().to_consensus(context)

    assert isinstance(consensus, ConsensusResult)
    assert consensus.trend == "BULLISH"
    assert consensus.signal == "BUY"
    assert consensus.confidence == 85.0


def test_operational_intelligence_adapter_rejects_none():
    try:
        OperationalIntelligenceAdapter().to_consensus(None)
    except ValueError as exc:
        assert str(exc) == "context must not be None"
    else:
        raise AssertionError("Expected ValueError")


def test_operational_intelligence_adapter_rejects_wrong_type():
    try:
        OperationalIntelligenceAdapter().to_consensus(object())
    except TypeError as exc:
        assert "OperationalIntelligenceContext" in str(exc)
    else:
        raise AssertionError("Expected TypeError")
