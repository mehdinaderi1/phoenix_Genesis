from analysis.multi_timeframe_pipeline import MultiTimeframePipeline
from core.database import DatabaseManager
from core.market_data.repository import MarketDataRepository
from core.market_data.source_manager import MarketDataSourceManager
from core.market_data.source_candle_pipeline import SourceCandlePipeline


class FakeSource:
    def __init__(self, candle, healthy=True):
        self.candle = candle
        self.healthy = healthy

    def connect(self):
        if not self.healthy:
            raise RuntimeError("source unavailable")
        return True

    def health_check(self):
        return self.healthy

    def get_price(self, symbol):
        return self.candle["close"]

    def get_candle(self, symbol, timeframe="1m"):
        if not self.healthy:
            raise RuntimeError("source unavailable")
        return self.candle

    def get_historical_candles(self, symbol, timeframe="1m", limit=30):
        return [self.candle]


def test_source_candle_pipeline_stores_real_source_candle(tmp_path):
    database = DatabaseManager(db_path=str(tmp_path / "phoenix.db"))
    database.connect()

    candle = {
        "timestamp": 2001,
        "open": 66000.0,
        "high": 66100.0,
        "low": 65900.0,
        "close": 66000.0,
        "volume": 12.0
    }

    manager = MarketDataSourceManager({
        "primary": FakeSource(candle)
    })

    pipeline = SourceCandlePipeline(manager, database)
    result = pipeline.fetch_and_store("BTCUSDT", "30m")

    assert result["stored"] is True
    assert result["source"] == "primary"
    assert result["candle"] == candle

    stored = database.get_candles()
    assert len(stored) == 1

    row = stored[0]
    assert row[1] == "BTCUSDT"
    assert row[2] == "30m"
    assert row[3] == 2001
    assert row[4] == 66000.0
    assert row[5] == 66100.0
    assert row[6] == 65900.0
    assert row[7] == 66000.0
    assert row[8] == 12.0

    database.close()


def test_source_candle_pipeline_uses_fallback_source(tmp_path):
    database = DatabaseManager(db_path=str(tmp_path / "phoenix.db"))
    database.connect()

    primary_candle = {
        "timestamp": 3001,
        "open": 66000.0,
        "high": 66100.0,
        "low": 65900.0,
        "close": 66000.0,
        "volume": 10.0
    }

    fallback_candle = {
        "timestamp": 3002,
        "open": 65500.0,
        "high": 65600.0,
        "low": 65400.0,
        "close": 65500.0,
        "volume": 11.0
    }

    manager = MarketDataSourceManager({
        "primary": FakeSource(primary_candle, healthy=False),
        "fallback": FakeSource(fallback_candle, healthy=True)
    })

    pipeline = SourceCandlePipeline(manager, database)
    result = pipeline.fetch_and_store("BTCUSDT", "30m")

    assert result["stored"] is True
    assert result["source"] == "fallback"
    assert result["candle"] == fallback_candle

    stored = database.get_candles()
    assert len(stored) == 1
    assert stored[0][1] == "BTCUSDT"
    assert stored[0][2] == "30m"
    assert stored[0][3] == 3002
    assert stored[0][7] == 65500.0

    database.close()


def test_source_candle_pipeline_returns_blind_when_no_source_available(tmp_path):
    database = DatabaseManager(db_path=str(tmp_path / "phoenix.db"))
    database.connect()

    candle = {
        "timestamp": 4001,
        "open": 65000.0,
        "high": 65100.0,
        "low": 64900.0,
        "close": 65000.0,
        "volume": 9.0
    }

    manager = MarketDataSourceManager({
        "primary": FakeSource(candle, healthy=False),
        "fallback": FakeSource(candle, healthy=False)
    })

    pipeline = SourceCandlePipeline(manager, database)
    result = pipeline.fetch_and_store("BTCUSDT", "30m")

    assert result["stored"] is False
    assert result["source"] is None
    assert result["candle"] is None

    stored = database.get_candles()
    assert stored == []

    database.close()


def test_source_candle_pipeline_feeds_mtf_from_database(tmp_path):
    database = DatabaseManager(db_path=str(tmp_path / "phoenix.db"))
    database.connect()

    repository = MarketDataRepository(database)

    for timeframe in ("30m", "4H", "1D"):
        for offset in range(5):
            timestamp = 5000 + (offset * 100)
            repository.save_candle(
                "BTCUSDT",
                timeframe,
                65000.0 + offset,
                65100.0 + offset,
                64900.0 + offset,
                65000.0 + offset,
                10.0,
                timestamp
            )

    bullish_candle = {
        "timestamp": 6000,
        "open": 65000.0,
        "high": 66100.0,
        "low": 64900.0,
        "close": 66000.0,
        "volume": 12.0
    }

    manager = MarketDataSourceManager({
        "primary": FakeSource(bullish_candle)
    })

    pipeline = SourceCandlePipeline(manager, database)
    result = pipeline.fetch_and_store("BTCUSDT", "30m")

    assert result["stored"] is True
    assert result["source"] == "primary"

    mtf = MultiTimeframePipeline(database)
    market_state = mtf.analyze("BTCUSDT")

    assert market_state.trend == "BULLISH"

    database.close()


def test_operational_market_context_runtime_uses_source_candle_pipeline(tmp_path):
    from core.market_data.operational_market_context_runtime import (
        OperationalMarketContextRuntime
    )

    database = DatabaseManager(db_path=str(tmp_path / "phoenix.db"))
    database.connect()

    repository = MarketDataRepository(database)

    for timeframe in ("30m", "4H", "1D"):
        for offset in range(5):
            repository.save_candle(
                "BTCUSDT",
                timeframe,
                65000.0 + offset,
                65100.0 + offset,
                64900.0 + offset,
                65000.0 + offset,
                10.0,
                7000 + (offset * 100)
            )

    source_candle = {
        "timestamp": 8000,
        "open": 65000.0,
        "high": 66100.0,
        "low": 64900.0,
        "close": 66000.0,
        "volume": 15.0
    }

    manager = MarketDataSourceManager({
        "primary": FakeSource(source_candle)
    })

    source_pipeline = SourceCandlePipeline(manager, database)

    observer = None

    runtime = OperationalMarketContextRuntime(
        database=database,
        source_candle_pipeline=source_pipeline
    )

    result = runtime.run_cycle(
        symbol="BTCUSDT",
        timeframes=("30m", "4H", "1D")
    )

    stored = database.get_candles()

    assert result["context"] is not None
    assert any(
        row[3] == 8000 and row[7] == 66000.0
        for row in stored
    )

    database.close()
