from core.database import DatabaseManager
from core.market_data.observer import RealMarketObserver
from core.market_data.operational_market_context_runtime import OperationalMarketContextRuntime
from core.market_data.pipeline import MarketDataPipeline
from core.market_data.source_manager import MarketDataSourceManager
from exchanges.mock_exchange import MockExchange


class RecoveringSource:
    def __init__(self):
        self.healthy = False

    def health_check(self):
        return self.healthy

    def connect(self):
        if not self.healthy:
            raise RuntimeError("source unavailable")
        return "Connected"

    def get_price(self, symbol):
        if not self.healthy:
            raise RuntimeError("source unavailable")
        return 65000.0

    def get_candle(self, symbol, timeframe="1m"):
        if not self.healthy:
            raise RuntimeError("source unavailable")
        return {
            "timestamp": 100,
            "open": 65000.0,
            "high": 65100.0,
            "low": 64900.0,
            "close": 65000.0,
            "volume": 10.0,
        }


def test_operational_runtime_recovers_from_blind(tmp_path):
    database = DatabaseManager(db_path=str(tmp_path / "phoenix.db"))
    database.connect()

    exchange = MockExchange()
    pipeline = MarketDataPipeline(exchange, database)

    source = RecoveringSource()
    source_manager = MarketDataSourceManager({
        "recovering": source,
    })

    observer = RealMarketObserver(source_manager)

    runtime = OperationalMarketContextRuntime(
        observer=observer,
        market_data_pipeline=pipeline,
        database=database,
    )

    first = runtime.run_cycle("BTCUSDT")

    assert first["observation"].source_status == "BLIND"
    assert first["context"] is None

    source.healthy = True

    second = runtime.run_cycle("BTCUSDT")

    assert second["observation"].source_status == "HEALTHY"
    assert second["observation"].price == 65000.0

    database.close()
