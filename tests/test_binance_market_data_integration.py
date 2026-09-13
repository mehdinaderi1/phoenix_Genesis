from exchanges.binance_exchange import BinanceExchange
from exchanges.exchange_manager import ExchangeManager
from core.engine import PhoenixEngine
from core.market_data.pipeline import MarketDataPipeline


def test_binance_exchange_integrates_with_market_data_pipeline(monkeypatch):
    engine = PhoenixEngine()
    engine.start()

    exchange = BinanceExchange()

    candle = [
        1752364800000,
        "64950.0",
        "65100.0",
        "64800.0",
        "65000.0",
        "125.5",
    ]

    def fake_request(path, params=None):
        if path == "/api/v3/ping":
            return {}

        if path == "/api/v3/klines":
            return [candle]

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
        engine.database
    )

    result = pipeline.fetch_and_store(
        symbol="BTCUSDT",
        timeframe="1m"
    )

    assert result["open"] == 64950.0
    assert result["high"] == 65100.0
    assert result["low"] == 64800.0
    assert result["close"] == 65000.0
    assert result["volume"] == 125.5
    assert result["timestamp"] == 1752364800

    cursor = engine.database.connection.cursor()

    cursor.execute("""
        SELECT symbol, timeframe, open, high, low, close, volume, timestamp
        FROM market_candles
        WHERE symbol=? AND timeframe=? AND timestamp=?
    """, ("BTCUSDT", "1m", 1752364800))

    stored = cursor.fetchone()

    assert stored is not None
    assert stored[0] == "BTCUSDT"
    assert stored[1] == "1m"
    assert stored[2] == 64950.0
    assert stored[3] == 65100.0
    assert stored[4] == 64800.0
    assert stored[5] == 65000.0
    assert stored[6] == 125.5
    assert stored[7] == 1752364800
