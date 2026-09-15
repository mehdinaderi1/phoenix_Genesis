from core.market_data.cross_source_validation_pipeline import CrossSourceValidationPipeline
from core.market_data.cross_source_validator import CrossSourceValidator
from core.market_data.source_manager import MarketDataSourceManager


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


def build_pipeline(binance_price, cmc_price, cmc_healthy=True):
    manager = MarketDataSourceManager({
        "binance": FakeSource(binance_price),
        "coinmarketcap": FakeSource(cmc_price, cmc_healthy),
    })
    validator = CrossSourceValidator(max_difference_percent=1.0)
    return CrossSourceValidationPipeline(manager, validator)


def test_pipeline_returns_valid_for_close_prices():
    pipeline = build_pipeline(65000.0, 65020.0)

    result = pipeline.validate("BTCUSDT")

    assert result.status == "VALID"
    assert result.primary_source == "binance"
    assert result.reference_source == "coinmarketcap"
    assert result.price == 65000.0


def test_pipeline_returns_suspect_for_divergent_prices():
    pipeline = build_pipeline(65000.0, 68000.0)

    result = pipeline.validate("BTCUSDT")

    assert result.status == "SUSPECT"
    assert result.difference_percent > 1.0


def test_pipeline_returns_insufficient_when_only_one_source_is_healthy():
    pipeline = build_pipeline(65000.0, 65020.0, cmc_healthy=False)

    result = pipeline.validate("BTCUSDT")

    assert result.status == "INSUFFICIENT"
    assert result.primary_source == "binance"
    assert result.reference_source is None


def test_pipeline_returns_blind_when_no_source_is_healthy():
    manager = MarketDataSourceManager({
        "binance": FakeSource(65000.0, healthy=False),
        "coinmarketcap": FakeSource(65020.0, healthy=False),
    })
    validator = CrossSourceValidator(max_difference_percent=1.0)
    pipeline = CrossSourceValidationPipeline(manager, validator)

    result = pipeline.validate("BTCUSDT")

    assert result.status == "BLIND"
    assert result.price is None
