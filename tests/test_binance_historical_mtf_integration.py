from core.database import DatabaseManager
from exchanges.binance_exchange import BinanceExchange
from exchanges.exchange_manager import ExchangeManager
from core.market_data.pipeline import MarketDataPipeline
from analysis.multi_timeframe_pipeline import MultiTimeframePipeline


def _make_binance_candles(base_price, count=30, start_timestamp=1900000000000, step=60000):
    candles = []
    for index in range(count):
        price = base_price + (index * 100)
        timestamp = start_timestamp + (index * step)
        candles.append([
            timestamp,
            str(price - 50),
            str(price + 100),
            str(price - 100),
            str(price),
            "125.5",
        ])
    return candles


def test_binance_historical_data_integrates_with_mtf_pipeline(monkeypatch, tmp_path):
    database_path = tmp_path / "binance_historical_mtf.db"

    database = DatabaseManager(db_path=str(database_path))
    database.connect()

    exchange = BinanceExchange()

    timeframe_prices = {
        "30m": 64000,
        "4h": 65000,
        "1d": 66000,
    }

    timeframe_offsets = {
        "30m": 0,
        "4h": 10000000,
        "1d": 20000000,
    }

    def fake_request(path, params=None):
        if path == "/api/v3/ping":
            return {}

        if path == "/api/v3/klines":
            interval = params["interval"]
            base_price = timeframe_prices[interval]
            start_timestamp = (
                1900000000000 + timeframe_offsets[interval]
            )

            return _make_binance_candles(
                base_price,
                30,
                start_timestamp
            )

        raise AssertionError(f"Unexpected path: {path}")

    monkeypatch.setattr(
        exchange,
        "_request",
        fake_request
    )

    manager = ExchangeManager()
    manager.set_exchange(exchange)

    assert manager.connect() == "Binance Connected"

    pipeline = MarketDataPipeline(
        manager,
        database
    )

    for timeframe in ("30m", "4H", "1D"):
        stored = pipeline.fetch_and_store_historical(
            symbol="BTCUSDT",
            timeframe=timeframe,
            limit=30
        )

        assert len(stored) == 30

    cursor = database.connection.cursor()

    cursor.execute("""
        SELECT timeframe, COUNT(*)
        FROM market_candles
        WHERE symbol=?
        GROUP BY timeframe
        ORDER BY timeframe
    """, ("BTCUSDT",))

    counts = dict(cursor.fetchall())

    assert counts["30m"] == 30
    assert counts["4H"] == 30
    assert counts["1D"] == 30

    mtf_pipeline = MultiTimeframePipeline(
        database
    )

    consensus = mtf_pipeline.analyze("BTCUSDT")

    assert consensus is not None
    assert hasattr(consensus, "trend")
    assert hasattr(consensus, "signal")
    assert hasattr(consensus, "confidence")

    database.close()
