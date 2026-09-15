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


def collect_prices(manager, symbol="BTCUSDT"):
    prices = {}

    for name in manager.sources:
        source = manager.get_source(name)
        if not source.health_check():
            continue
        prices[name] = source.get_price(symbol)

    return prices


def test_source_manager_prices_can_be_validated():
    manager = MarketDataSourceManager({
        "binance": FakeSource(65000.0),
        "coinmarketcap": FakeSource(65020.0),
    })
    manager.set_primary_source("binance")

    validator = CrossSourceValidator(max_difference_percent=1.0)
    prices = collect_prices(manager)
    result = validator.validate(prices)

    assert result.status == "VALID"
    assert result.primary_source == "binance"
    assert result.reference_source == "coinmarketcap"


def test_source_manager_prices_can_be_flagged_suspect():
    manager = MarketDataSourceManager({
        "binance": FakeSource(65000.0),
        "coinmarketcap": FakeSource(68000.0),
    })
    manager.set_primary_source("binance")

    validator = CrossSourceValidator(max_difference_percent=1.0)
    prices = collect_prices(manager)
    result = validator.validate(prices)

    assert result.status == "SUSPECT"
    assert result.primary_source == "binance"
    assert result.reference_source == "coinmarketcap"


def test_source_manager_single_healthy_source_is_insufficient():
    manager = MarketDataSourceManager({
        "binance": FakeSource(65000.0),
        "coinmarketcap": FakeSource(65020.0, healthy=False),
    })
    manager.set_primary_source("binance")

    validator = CrossSourceValidator(max_difference_percent=1.0)
    prices = collect_prices(manager)
    result = validator.validate(prices)

    assert result.status == "INSUFFICIENT"
    assert result.primary_source == "binance"
    assert result.reference_source is None
    assert result.price == 65000.0
