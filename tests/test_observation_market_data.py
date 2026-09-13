from core.database import DatabaseManager
from core.market_data.observation_market_data import ObservationMarketDataBridge
from core.market_data.observer import RealMarketObserver
from core.market_data.pipeline import MarketDataPipeline
from core.market_data.source_manager import MarketDataSourceManager
from exchanges.mock_exchange import MockExchange


def test_observation_market_data_bridge_stores_fresh_candle(tmp_path):
    database = DatabaseManager(db_path=str(tmp_path / "phoenix.db"))
    database.connect()
    exchange = MockExchange()

    exchange.set_price_sequence(
        "BTCUSDT",
        [65000.0, 65500.0, 66000.0]
    )

    exchange.set_candle_sequence(
        "BTCUSDT",
        "1m",
        [
            {
                "timestamp": 1001,
                "open": 64900.0,
                "high": 65100.0,
                "low": 64800.0,
                "close": 65000.0,
                "volume": 10.0
            },
            {
                "timestamp": 1002,
                "open": 65400.0,
                "high": 65600.0,
                "low": 65300.0,
                "close": 65500.0,
                "volume": 11.0
            },
            {
                "timestamp": 1003,
                "open": 65900.0,
                "high": 66100.0,
                "low": 65800.0,
                "close": 66000.0,
                "volume": 12.0
            }
        ]
    )

    class Source:
        def __init__(self, exchange):
            self.exchange = exchange

        def connect(self):
            return True

        def health_check(self):
            return True

        def get_price(self, symbol):
            return self.exchange.get_price(symbol)

    source = Source(exchange)
    manager = MarketDataSourceManager({"mock": source})
    observer = RealMarketObserver(manager)
    pipeline = MarketDataPipeline(exchange, database)
    bridge = ObservationMarketDataBridge(observer, pipeline)

    first = bridge.observe_and_store()
    second = bridge.observe_and_store()
    third = bridge.observe_and_store()

    assert first["observation"].price == 65000.0
    assert second["observation"].price == 65500.0
    assert third["observation"].price == 66000.0

    assert first["candle"]["close"] == 65000.0
    assert second["candle"]["close"] == 65500.0
    assert third["candle"]["close"] == 66000.0

    assert first["stored"] is True
    assert second["stored"] is True
    assert third["stored"] is True

    rows = database.connection.execute(
        "SELECT close FROM market_candles "
        "WHERE symbol = ? AND timeframe = ? "
        "ORDER BY timestamp",
        ("BTCUSDT", "1m")
    ).fetchall()

    assert [row[0] for row in rows] == [65000.0, 65500.0, 66000.0]

    database.close()


def test_observation_market_data_bridge_does_not_store_when_blind(tmp_path):
    database = DatabaseManager(db_path=str(tmp_path / "phoenix.db"))
    database.connect()
    exchange = MockExchange()

    class Source:
        def connect(self):
            raise RuntimeError("source unavailable")

        def health_check(self):
            return False

        def get_price(self, symbol):
            raise RuntimeError("source unavailable")

    manager = MarketDataSourceManager({"broken": Source()})
    observer = RealMarketObserver(manager)
    pipeline = MarketDataPipeline(exchange, database)
    bridge = ObservationMarketDataBridge(observer, pipeline)

    result = bridge.observe_and_store()

    assert result["observation"].source_status == "BLIND"
    assert result["observation"].price is None
    assert result["candle"] is None
    assert result["stored"] is False

    rows = database.connection.execute(
        "SELECT COUNT(*) FROM market_candles"
    ).fetchone()

    assert rows[0] == 0

    database.close()
