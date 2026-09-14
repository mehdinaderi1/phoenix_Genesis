from intelligence.consensus import ConsensusResult
from core.market_data.operational_market_context import OperationalMarketContext
from core.market_data.operational_market_context_builder import OperationalMarketContextBuilder


def test_operational_market_context_builder_maps_mtf_result():
    consensus = ConsensusResult(
        trend="BULLISH",
        signal="BUY",
        confidence=82.5
    )

    context = OperationalMarketContextBuilder().build(
        "BTCUSDT",
        consensus
    )

    assert isinstance(context, OperationalMarketContext)
    assert context.symbol == "BTCUSDT"
    assert context.trend == "BULLISH"
    assert context.signal == "BUY"
    assert context.confidence == 82.5
    assert context.timestamp

    assert context.summary() == {
        "symbol": "BTCUSDT",
        "trend": "BULLISH",
        "signal": "BUY",
        "confidence": 82.5,
        "timestamp": context.timestamp
    }


def test_operational_market_context_builder_rejects_missing_consensus():
    builder = OperationalMarketContextBuilder()

    try:
        builder.build("BTCUSDT", None)
    except ValueError as exc:
        assert str(exc) == "consensus must not be None"
    else:
        raise AssertionError("Expected ValueError")
