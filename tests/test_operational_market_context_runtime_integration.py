from core.database import DatabaseManager
from core.market_data.market_data import MarketData
from core.market_data.observer import RealMarketObserver
from core.market_data.operational_market_context import OperationalMarketContext
from core.market_data.operational_market_context_runtime import OperationalMarketContextRuntime
from core.market_data.pipeline import MarketDataPipeline
from core.market_data.source_manager import MarketDataSourceManager
from exchanges.mock_exchange import MockExchange


class MockSource:
    def __init__(self, exchange):
        self.exchange = exchange

    def connect(self):
        return True

    def health_check(self):
        return True

    def get_price(self, symbol):
        return self.exchange.get_price(symbol)


def test_operational_runtime_reacts_to_changing_market_data(tmp_path):
    database = DatabaseManager(db_path=str(tmp_path / "phoenix.db"))
    database.connect()

    exchange = MockExchange()
    exchange.set_price_sequence(
        "BTCUSDT",
        [66000.0, 64000.0, 63000.0]
    )

    baseline = [65000.0] * 5

    for timeframe in ("30m", "4H", "1D"):
        for index, price in enumerate(baseline):
            database.connection.execute(
                "INSERT INTO market_candles "
                "(symbol, timeframe, timestamp, open, high, low, close, volume) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    "BTCUSDT",
                    timeframe,
                    index + 1,
                    price,
                    price + 100.0,
                    price - 100.0,
                    price,
                    10.0
                )
            )

    database.connection.commit()

    observation_prices = [66000.0, 64000.0, 63000.0]

    for timeframe in ("30m", "4H", "1D"):
        candles = []
        for index, price in enumerate(observation_prices):
            candles.append({
                "timestamp": 100 + index,
                "open": price,
                "high": price + 100.0,
                "low": price - 100.0,
                "close": price,
                "volume": 10.0 + index
            })
        exchange.set_candle_sequence("BTCUSDT", timeframe, candles)

    manager = MarketDataSourceManager({
        "mock": MockSource(exchange)
    })

    observer = RealMarketObserver(manager)
    market_data_pipeline = MarketDataPipeline(exchange, database)

    runtime = OperationalMarketContextRuntime(
        observer,
        market_data_pipeline,
        database
    )

    contexts = runtime.run("BTCUSDT", cycles=3)

    assert len(contexts) == 3
    assert all(isinstance(context, OperationalMarketContext) for context in contexts)

    assert contexts[0].trend == "BULLISH"
    assert contexts[0].signal == "WAIT"

    assert contexts[1].trend == "BEARISH"
    assert contexts[1].signal == "WAIT"

    assert contexts[2].trend == "BEARISH"
    assert contexts[2].signal == "WAIT"

    assert contexts[0].trend != contexts[2].trend

    database.close()
