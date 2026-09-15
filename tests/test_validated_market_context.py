from core.market_data.validated_market_context import ValidatedMarketContext
from core.market_data.cross_source_validator import CrossSourceValidationResult
from core.market_data.operational_market_context import OperationalMarketContext


def test_validated_market_context_contains_context_and_validation():
    context = OperationalMarketContext(
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

    validated = ValidatedMarketContext(
        context=context,
        validation=validation,
    )

    assert validated.context is context
    assert validated.validation is validation
    assert validated.context.symbol == "BTCUSDT"
    assert validated.validation.status == "VALID"
