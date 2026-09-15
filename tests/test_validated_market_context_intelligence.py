from core.market_data.operational_intelligence_context import OperationalIntelligenceContext
from core.market_data.operational_intelligence_context_builder import OperationalIntelligenceContextBuilder
from core.market_data.validated_market_context import ValidatedMarketContext
from core.market_data.operational_market_context import OperationalMarketContext
from core.market_data.cross_source_validator import CrossSourceValidationResult


def test_validated_market_context_can_feed_operational_intelligence_context():
    market_context = OperationalMarketContext(
        symbol="BTCUSDT",
        trend="BULLISH",
        signal="BUY",
        confidence=85.0,
        timestamp="2026-01-01T00:00:00+00:00",
    )

    validation = CrossSourceValidationResult(
        status="VALID",
        primary_source="binance",
        reference_source="coinmarketcap",
        price=65000.0,
        difference_percent=0.03,
    )

    validated_context = ValidatedMarketContext(
        context=market_context,
        validation=validation,
    )

    builder = OperationalIntelligenceContextBuilder()
    intelligence_context = builder.build(validated_context.context)

    assert isinstance(
        intelligence_context,
        OperationalIntelligenceContext
    )
    assert intelligence_context.symbol == "BTCUSDT"
    assert intelligence_context.trend == "BULLISH"
    assert intelligence_context.signal == "BUY"
    assert intelligence_context.confidence == 85.0
