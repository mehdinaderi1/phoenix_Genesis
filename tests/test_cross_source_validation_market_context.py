from core.market_data.cross_source_validation_pipeline import CrossSourceValidationPipeline
from core.market_data.cross_source_validator import CrossSourceValidator
from core.market_data.source_manager import MarketDataSourceManager
from core.market_data.operational_market_context import OperationalMarketContext


class FakeSource:
    def __init__(self, price, healthy=True):
        self.price = price
        self.healthy = healthy

    def health_check(self):
        return self.healthy

    def connect(self):
        return True

    def get_price(self, symbol):
        return self.price


class FakeMarketContextBuilder:
    def build(self, symbol, validation_result):
        if validation_result.status == "SUSPECT":
            return None

        if validation_result.status == "BLIND":
            return None

        return OperationalMarketContext(
            symbol=symbol,
            trend="BULLISH",
            signal="BUY",
            confidence=85.0,
            timestamp="2026-01-01T00:00:00+00:00"
        )


def build_validation_pipeline(binance_price, cmc_price, cmc_healthy=True):
    manager = MarketDataSourceManager({
        "binance": FakeSource(binance_price),
        "coinmarketcap": FakeSource(cmc_price, cmc_healthy),
    })
    validator = CrossSourceValidator(max_difference_percent=1.0)
    return CrossSourceValidationPipeline(manager, validator)


def test_valid_cross_source_data_allows_market_context():
    pipeline = build_validation_pipeline(65000.0, 65020.0)
    result = pipeline.validate("BTCUSDT")

    builder = FakeMarketContextBuilder()
    context = builder.build("BTCUSDT", result)

    assert result.status == "VALID"
    assert context is not None
    assert context.symbol == "BTCUSDT"


def test_suspect_cross_source_data_blocks_market_context():
    pipeline = build_validation_pipeline(65000.0, 68000.0)
    result = pipeline.validate("BTCUSDT")

    builder = FakeMarketContextBuilder()
    context = builder.build("BTCUSDT", result)

    assert result.status == "SUSPECT"
    assert context is None


def test_insufficient_cross_source_data_allows_context_with_single_source():
    pipeline = build_validation_pipeline(
        65000.0,
        65020.0,
        cmc_healthy=False
    )
    result = pipeline.validate("BTCUSDT")

    builder = FakeMarketContextBuilder()
    context = builder.build("BTCUSDT", result)

    assert result.status == "INSUFFICIENT"
    assert context is not None


def test_blind_cross_source_data_blocks_market_context():
    manager = MarketDataSourceManager({
        "binance": FakeSource(65000.0, healthy=False),
        "coinmarketcap": FakeSource(65020.0, healthy=False),
    })
    validator = CrossSourceValidator(max_difference_percent=1.0)
    pipeline = CrossSourceValidationPipeline(manager, validator)

    result = pipeline.validate("BTCUSDT")

    builder = FakeMarketContextBuilder()
    context = builder.build("BTCUSDT", result)

    assert result.status == "BLIND"
    assert context is None
