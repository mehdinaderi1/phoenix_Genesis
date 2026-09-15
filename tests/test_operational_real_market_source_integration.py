from core.database import DatabaseManager
from core.market_data.market_data import MarketData
from core.market_data.observer import RealMarketObserver
from core.market_data.operational_market_context_runtime import OperationalMarketContextRuntime
from core.market_data.pipeline import MarketDataPipeline
from core.market_data.source_manager import MarketDataSourceManager
from exchanges.mock_exchange import MockExchange


class FakeSource:
    def __init__(self, price=65000.0, healthy=True, name="source"):
        self.price = price
        self.healthy = healthy
        self.name = name

    def connect(self):
        if not self.healthy:
            raise RuntimeError(f"{self.name} unavailable")
        return True

    def health_check(self):
        return self.healthy

    def get_price(self, symbol):
        if not self.healthy:
            raise RuntimeError(f"{self.name} unavailable")
        return self.price


def build_runtime(tmp_path, primary, fallback):
    database = DatabaseManager(db_path=str(tmp_path / "phoenix.db"))
    database.connect()

    exchange = MockExchange()
    candle = {
        "timestamp": 1001,
        "open": 65000.0,
        "high": 65100.0,
        "low": 64900.0,
        "close": 65000.0,
        "volume": 10.0,
    }

    for timeframe in ("30m", "4H", "1D"):
        exchange.set_candle_sequence(
            "BTCUSDT",
            timeframe,
            [candle]
        )

    pipeline = MarketDataPipeline(exchange, database)
    manager = MarketDataSourceManager({
        "primary": primary,
        "fallback": fallback,
    })
    manager.set_primary_source("primary")

    observer = RealMarketObserver(manager)
    runtime = OperationalMarketContextRuntime(
        observer=observer,
        market_data_pipeline=pipeline,
        database=database,
    )

    return database, runtime


def test_operational_real_market_primary_source(tmp_path):
    primary = FakeSource(price=65000.0, healthy=True, name="primary")
    fallback = FakeSource(price=64000.0, healthy=True, name="fallback")

    database, runtime = build_runtime(tmp_path, primary, fallback)

    result = runtime.run_cycle(symbol="BTCUSDT")

    assert result["observation"].source == "primary"
    assert result["observation"].price == 65000.0
    assert result["observation"].fallback_used is False
    assert result["observation"].source_status == "HEALTHY"
    assert result["context"] is not None

    database.close()


def test_operational_real_market_fallback_source(tmp_path):
    primary = FakeSource(price=65000.0, healthy=False, name="primary")
    fallback = FakeSource(price=64000.0, healthy=True, name="fallback")

    database, runtime = build_runtime(tmp_path, primary, fallback)

    result = runtime.run_cycle(symbol="BTCUSDT")

    assert result["observation"].source == "fallback"
    assert result["observation"].price == 64000.0
    assert result["observation"].fallback_used is True
    assert result["observation"].source_status == "HEALTHY"
    assert result["context"] is not None

    database.close()


def test_operational_real_market_blind_blocks_context(tmp_path):
    primary = FakeSource(price=65000.0, healthy=False, name="primary")
    fallback = FakeSource(price=64000.0, healthy=False, name="fallback")

    database, runtime = build_runtime(tmp_path, primary, fallback)

    result = runtime.run_cycle(symbol="BTCUSDT")

    assert result["observation"].source is None
    assert result["observation"].price is None
    assert result["observation"].fallback_used is False
    assert result["observation"].source_status == "BLIND"
    assert result["context"] is None

    database.close()
