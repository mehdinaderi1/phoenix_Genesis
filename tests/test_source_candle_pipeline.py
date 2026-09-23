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

def test_source_candle_pipeline_stores_historical_candles(tmp_path):
    database = DatabaseManager(db_path=str(tmp_path / "phoenix.db"))
    database.connect()

    candles = [
        {
            "timestamp": 5000,
            "open": 65000.0,
            "high": 65100.0,
            "low": 64900.0,
            "close": 65000.0,
            "volume": 10.0
        },
        {
            "timestamp": 5300,
            "open": 65000.0,
            "high": 65200.0,
            "low": 64950.0,
            "close": 65100.0,
            "volume": 11.0
        },
        {
            "timestamp": 5600,
            "open": 65100.0,
            "high": 65300.0,
            "low": 65000.0,
            "close": 65200.0,
            "volume": 12.0
        }
    ]

    class HistoricalFakeSource(FakeSource):
        def get_historical_candles(
            self,
            symbol,
            timeframe="1m",
            limit=30
        ):
            assert symbol == "BTCUSDT"
            assert timeframe == "5m"
            assert limit == 3
            return candles

    manager = MarketDataSourceManager({
        "primary": HistoricalFakeSource(candles[0])
    })

    pipeline = SourceCandlePipeline(manager, database)

    result = pipeline.fetch_and_store_historical(
        "BTCUSDT",
        "5m",
        limit=3
    )

    assert result["source"] == "primary"
    assert result["fetched"] == 3
    assert result["stored"] == 3

    stored = database.get_candles()

    assert len(stored) == 3
    assert [row[3] for row in stored] == [5000, 5300, 5600]

    database.close()


def test_source_candle_pipeline_historical_is_duplicate_safe(tmp_path):
    database = DatabaseManager(db_path=str(tmp_path / "phoenix.db"))
    database.connect()

    candle = {
        "timestamp": 6000,
        "open": 65000.0,
        "high": 65100.0,
        "low": 64900.0,
        "close": 65000.0,
        "volume": 10.0
    }

    manager = MarketDataSourceManager({
        "primary": FakeSource(candle)
    })

    pipeline = SourceCandlePipeline(manager, database)

    first = pipeline.fetch_and_store_historical(
        "BTCUSDT",
        "5m",
        limit=1
    )

    second = pipeline.fetch_and_store_historical(
        "BTCUSDT",
        "5m",
        limit=1
    )

    assert first["fetched"] == 1
    assert first["stored"] == 1

    assert second["fetched"] == 1
    assert second["stored"] == 0

    assert len(database.get_candles()) == 1

    database.close()


def test_source_candle_pipeline_historical_uses_fallback(tmp_path):
    database = DatabaseManager(db_path=str(tmp_path / "phoenix.db"))
    database.connect()

    candle = {
        "timestamp": 7000,
        "open": 65000.0,
        "high": 65100.0,
        "low": 64900.0,
        "close": 65000.0,
        "volume": 10.0
    }

    manager = MarketDataSourceManager({
        "primary": FakeSource(candle, healthy=False),
        "fallback": FakeSource(candle, healthy=True)
    })

    pipeline = SourceCandlePipeline(manager, database)

    result = pipeline.fetch_and_store_historical(
        "BTCUSDT",
        "15m",
        limit=5
    )

    assert result["source"] == "fallback"
    assert result["fetched"] == 1
    assert result["stored"] == 1

    database.close()


def test_source_candle_pipeline_historical_zero_limit(tmp_path):
    database = DatabaseManager(db_path=str(tmp_path / "phoenix.db"))
    database.connect()

    candle = {
        "timestamp": 8000,
        "open": 65000.0,
        "high": 65100.0,
        "low": 64900.0,
        "close": 65000.0,
        "volume": 10.0
    }

    manager = MarketDataSourceManager({
        "primary": FakeSource(candle)
    })

    pipeline = SourceCandlePipeline(manager, database)

    result = pipeline.fetch_and_store_historical(
        "BTCUSDT",
        "5m",
        limit=0
    )

    assert result["source"] is None
    assert result["fetched"] == 0
    assert result["stored"] == 0
    assert database.get_candles() == []

    database.close()

def test_source_candle_pipeline_historical_xt_integration(tmp_path):
    from exchanges.xt_exchange import XTExchange

    database = DatabaseManager(db_path=str(tmp_path / "phoenix.db"))
    database.connect()

    xt = XTExchange(timeout=1)

    xt_response = {
        "result": [
            {
                "t": 1790160300000,
                "o": "85860",
                "h": "85900",
                "l": "85800",
                "c": "85880",
                "v": "1000"
            },
            {
                "t": 1790160600000,
                "o": "85880",
                "h": "85950",
                "l": "85850",
                "c": "85920",
                "v": "1100"
            },
            {
                "t": 1790160900000,
                "o": "85920",
                "h": "86000",
                "l": "85900",
                "c": "85980",
                "v": "1200"
            }
        ]
    }

    def fake_request(path, params=None):
        if path == "/v4/public/ticker/price":
            return {
                "result": [
                    {"p": "85880"}
                ]
            }

        if path == "/v4/public/kline":
            return xt_response

        raise AssertionError(f"Unexpected XT path: {path}")

    xt._request = fake_request

    manager = MarketDataSourceManager({
        "xt": xt
    })

    pipeline = SourceCandlePipeline(manager, database)

    result = pipeline.fetch_and_store_historical(
        "BTCUSDT",
        "5m",
        limit=3
    )

    assert result["source"] == "xt"
    assert result["fetched"] == 3
    assert result["stored"] == 3

    stored = database.get_candles()

    assert len(stored) == 3
    assert [row[3] for row in stored] == [
        1790160300,
        1790160600,
        1790160900
    ]

    assert [row[7] for row in stored] == [
        85880.0,
        85920.0,
        85980.0
    ]

    database.close()

def test_source_candle_pipeline_warm_up_multiple_timeframes(tmp_path):
    database = DatabaseManager(db_path=str(tmp_path / "phoenix.db"))
    database.connect()

    candles = {
        "5m": {
            "timestamp": 9000,
            "open": 65000.0,
            "high": 65100.0,
            "low": 64900.0,
            "close": 65000.0,
            "volume": 10.0
        },
        "15m": {
            "timestamp": 9900,
            "open": 65100.0,
            "high": 65200.0,
            "low": 65000.0,
            "close": 65150.0,
            "volume": 11.0
        },
        "30m": {
            "timestamp": 10800,
            "open": 65200.0,
            "high": 65300.0,
            "low": 65100.0,
            "close": 65250.0,
            "volume": 12.0
        },
        "4H": {
            "timestamp": 14400,
            "open": 65300.0,
            "high": 65400.0,
            "low": 65200.0,
            "close": 65350.0,
            "volume": 13.0
        },
        "1D": {
            "timestamp": 86400,
            "open": 65400.0,
            "high": 65500.0,
            "low": 65300.0,
            "close": 65450.0,
            "volume": 14.0
        }
    }

    class WarmupFakeSource(FakeSource):
        def get_historical_candles(
            self,
            symbol,
            timeframe="1m",
            limit=30
        ):
            return [candles[timeframe]]

    manager = MarketDataSourceManager({
        "primary": WarmupFakeSource(candles["5m"])
    })

    pipeline = SourceCandlePipeline(manager, database)

    result = pipeline.warm_up(
        symbol="BTCUSDT",
        timeframes=("5m", "15m", "30m", "4H", "1D"),
        limit=30
    )

    assert set(result) == {"5m", "15m", "30m", "4H", "1D"}

    for timeframe in result:
        assert result[timeframe]["source"] == "primary"
        assert result[timeframe]["fetched"] == 1
        assert result[timeframe]["stored"] == 1

    stored = database.get_candles()

    assert len(stored) == 5
    assert {row[2] for row in stored} == {
        "5m", "15m", "30m", "4H", "1D"
    }

    database.close()

def test_source_candle_pipeline_warm_up_feeds_operational_mtf(tmp_path):
    database = DatabaseManager(db_path=str(tmp_path / "phoenix.db"))
    database.connect()

    candles = {}

    for timeframe in ("5m", "15m", "30m", "4H", "1D"):
        candles[timeframe] = []

        for offset in range(5):
            candles[timeframe].append({
                "timestamp": 10000 + offset + (
                    100000 if timeframe == "4H" else
                    200000 if timeframe == "1D" else
                    0
                ),
                "open": 65000.0 + offset,
                "high": 65100.0 + offset,
                "low": 64900.0 + offset,
                "close": 65000.0 + offset,
                "volume": 10.0 + offset
            })

    class WarmupMTFFakeSource(FakeSource):
        def get_historical_candles(
            self,
            symbol,
            timeframe="1m",
            limit=30
        ):
            return candles[timeframe]

        def get_candle(self, symbol, timeframe="1m"):
            return candles[timeframe][-1]

    manager = MarketDataSourceManager({
        "primary": WarmupMTFFakeSource(candles["5m"][0])
    })

    pipeline = SourceCandlePipeline(manager, database)

    warmup = pipeline.warm_up(
        symbol="BTCUSDT",
        timeframes=("5m", "15m", "30m", "4H", "1D"),
        limit=5
    )

    assert set(warmup) == {
        "5m", "15m", "30m", "4H", "1D"
    }

    assert all(
        warmup[timeframe]["source"] == "primary"
        for timeframe in warmup
    )

    assert all(
        warmup[timeframe]["fetched"] == 5
        for timeframe in warmup
    )

    assert all(
        warmup[timeframe]["stored"] == 5
        for timeframe in warmup
    )

    from analysis.multi_timeframe_pipeline import MultiTimeframePipeline

    mtf = MultiTimeframePipeline(database)
    market_state = mtf.analyze(
        "BTCUSDT",
        timeframes=("5m", "15m", "30m", "4H", "1D")
    )

    assert market_state is not None

    from market.market_data_reader import MarketDataReader

    reader = MarketDataReader(database)

    for timeframe in ("5m", "15m", "30m", "4H", "1D"):
        assert len(
            reader.get_close_prices(
                "BTCUSDT",
                timeframe
            )
        ) == 5

    database.close()
def test_source_candle_pipeline_warm_up_is_consumed_by_operational_runtime(tmp_path):
    from core.market_data.operational_market_context_runtime import (
        OperationalMarketContextRuntime
    )
    from market.market_data_reader import MarketDataReader

    database = DatabaseManager(
        db_path=str(tmp_path / "phoenix.db")
    )
    database.connect()

    candles = {}

    for timeframe in ("5m", "15m", "30m", "4H", "1D"):
        candles[timeframe] = []

        for offset in range(5):
            candles[timeframe].append({
                "timestamp": (
                    10000
                    + offset
                    + (
                        100000 if timeframe == "4H"
                        else 200000 if timeframe == "1D"
                        else 0
                    )
                ),
                "open": 65000.0 + offset,
                "high": 65100.0 + offset,
                "low": 64900.0 + offset,
                "close": 65000.0 + offset,
                "volume": 10.0 + offset
            })

    class RuntimeWarmupFakeSource(FakeSource):
        def get_historical_candles(
            self,
            symbol,
            timeframe="1m",
            limit=30
        ):
            return candles[timeframe]

        def get_candle(self, symbol, timeframe="1m"):
            return candles[timeframe][-1]

    source = RuntimeWarmupFakeSource(candles["5m"][0])

    manager = MarketDataSourceManager({
        "primary": source
    })

    pipeline = SourceCandlePipeline(
        manager,
        database
    )

    warmup = pipeline.warm_up(
        symbol="BTCUSDT",
        timeframes=("5m", "15m", "30m", "4H", "1D"),
        limit=5
    )

    assert all(
        warmup[timeframe]["stored"] == 5
        for timeframe in warmup
    )

    runtime = OperationalMarketContextRuntime(
        database=database,
        source_candle_pipeline=pipeline
    )

    result = runtime.run_cycle(
        symbol="BTCUSDT",
        timeframes=("5m", "15m", "30m", "4H", "1D")
    )

    assert result["context"] is not None

    reader = MarketDataReader(database)

    for timeframe in ("5m", "15m", "30m", "4H", "1D"):
        prices = reader.get_close_prices(
            "BTCUSDT",
            timeframe
        )

        assert len(prices) >= 5

    database.close()
