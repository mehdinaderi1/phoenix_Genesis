from types import SimpleNamespace

from core.market_data.operational_intelligence_context import OperationalIntelligenceContext
from core.market_data.operational_intelligence_context_builder import OperationalIntelligenceContextBuilder


def test_operational_intelligence_context_builder_creates_context():
    market_context = SimpleNamespace(
        symbol="BTCUSDT",
        trend="BULLISH",
        signal="BUY",
        confidence=85.0
    )

    context = OperationalIntelligenceContextBuilder().build(
        market_context
    )

    assert isinstance(context, OperationalIntelligenceContext)
    assert context.symbol == "BTCUSDT"
    assert context.trend == "BULLISH"
    assert context.signal == "BUY"
    assert context.confidence == 85.0


def test_operational_intelligence_context_summary():
    context = OperationalIntelligenceContext(
        symbol="BTCUSDT",
        trend="BEARISH",
        signal="SELL",
        confidence=35.0
    )

    assert context.summary() == {
        "symbol": "BTCUSDT",
        "trend": "BEARISH",
        "signal": "SELL",
        "confidence": 35.0
    }


def test_operational_intelligence_context_builder_rejects_none():
    builder = OperationalIntelligenceContextBuilder()

    try:
        builder.build(None)
    except ValueError as exc:
        assert str(exc) == "market_context must not be None"
    else:
        raise AssertionError("Expected ValueError")
