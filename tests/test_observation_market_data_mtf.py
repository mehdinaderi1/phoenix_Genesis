from core.database import DatabaseManager
from core.market_data.observation_market_data import ObservationMarketDataBridge
from core.market_data.observer import RealMarketObserver
from core.market_data.pipeline import MarketDataPipeline
from core.market_data.source_manager import MarketDataSourceManager
from analysis.multi_timeframe_pipeline import MultiTimeframePipeline
from exchanges.mock_exchange import MockExchange


def test_observation_market_data_flows_into_mtf(tmp_path):
    database = DatabaseManager(db_path=str(tmp_path / "phoenix.db"))
    database.connect()

    exchange = MockExchange()

    exchange.set_price_sequence(
        "BTCUSDT",
        [66000.0, 64000.0, 63000.0]
    )

    baseline = [65000.0] * 5
    observation_prices = [66000.0, 64000.0, 63000.0]

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

    class Source:
        def __init__(self, exchange):
            self.exchange = exchange

        def connect(self):
            return True

        def health_check(self):
            return True

        def get_price(self, symbol):
            return self.exchange.get_price(symbol)

    manager = MarketDataSourceManager({"mock": Source(exchange)})
    observer = RealMarketObserver(manager)
    pipeline = MarketDataPipeline(exchange, database)
    bridge = ObservationMarketDataBridge(observer, pipeline)
    mtf_pipeline = MultiTimeframePipeline(database)

    results = []

    for _ in range(3):
        for timeframe in ("30m", "4H", "1D"):
            result = bridge.observe_and_store(
                symbol="BTCUSDT",
                timeframe=timeframe
            )
            assert result["stored"] is True

        results.append(mtf_pipeline.analyze("BTCUSDT"))

    assert len(results) == 3
    assert all(result is not None for result in results)
    assert results[0].trend == "BULLISH"
    assert results[1].trend == "BEARISH"
    assert results[2].trend == "BEARISH"
    assert results[0].trend != results[2].trend

    database.close()
