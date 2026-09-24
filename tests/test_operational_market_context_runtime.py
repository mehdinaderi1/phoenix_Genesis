from core.database import DatabaseManager
from core.market_data.operational_market_context import OperationalMarketContext
from core.market_data.operational_market_context_runtime import OperationalMarketContextRuntime


def test_operational_market_context_runtime_returns_contexts(tmp_path, capsys):
    database = DatabaseManager(db_path=str(tmp_path / "phoenix.db"))
    database.connect()

    for timeframe in ("30m", "4H", "1D"):
        for index, price in enumerate([65000.0] * 5):
            database.connection.execute(
                "INSERT INTO market_candles "
                "(symbol, timeframe, timestamp, open, high, low, close, volume) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                ("BTCUSDT", timeframe, index + 1, price, price + 100.0, price - 100.0, price, 10.0)
            )

    database.connection.commit()

    runtime = OperationalMarketContextRuntime(database)
    contexts = runtime.run("BTCUSDT", cycles=2)

    assert len(contexts) == 2
    assert all(isinstance(context, OperationalMarketContext) for context in contexts)
    assert contexts[0].symbol == "BTCUSDT"
    assert contexts[0].trend == "NEUTRAL"
    assert contexts[0].signal == "WAIT"
    assert contexts[0].confidence == 50.0
    assert contexts[0].timestamp

    output = capsys.readouterr().out
    assert output.count("[MARKET] BTCUSDT") == 2
    assert "trend=NEUTRAL" in output
    assert "signal=WAIT" in output

    database.close()


def test_operational_market_context_runtime_rejects_invalid_cycles(tmp_path):
    database = DatabaseManager(db_path=str(tmp_path / "phoenix.db"))
    database.connect()

    runtime = OperationalMarketContextRuntime(database)

    try:
        runtime.run("BTCUSDT", cycles=0)
    except ValueError as exc:
        assert str(exc) == "cycles must be greater than zero"
    else:
        raise AssertionError("Expected ValueError")

    database.close()



def test_operational_market_context_runtime_passes_custom_timeframes(
    tmp_path
):
    database = DatabaseManager(
        db_path=str(tmp_path / "custom_timeframes.db")
    )
    database.connect()

    runtime = OperationalMarketContextRuntime(database)

    captured = {}

    def fake_build(symbol, timeframes=None):
        captured["symbol"] = symbol
        captured["timeframes"] = timeframes

        return OperationalMarketContext(
            symbol=symbol,
            trend="BULLISH",
            signal="BUY",
            confidence=80.0,
            timestamp="test"
        )

    runtime.context_pipeline.build = fake_build

    timeframes = (
        "5m",
        "15m",
        "30m",
        "4H",
        "1D"
    )

    result = runtime.run_cycle(
        symbol="BTCUSDT",
        timeframes=timeframes
    )

    assert result["context"] is not None
    assert captured["symbol"] == "BTCUSDT"
    assert captured["timeframes"] == timeframes

    database.close()


def test_operational_market_context_runtime_reuses_source_health_within_cycle(
    tmp_path
):
    database = DatabaseManager(
        db_path=str(tmp_path / "health_reuse.db")
    )
    database.connect()

    class FakeSource:
        def __init__(self):
            self.health_check_calls = 0

        def health_check(self):
            self.health_check_calls += 1
            return True

    source = FakeSource()

    class FakeObserver:
        def observe(self, symbol, _health_cache=None):
            if _health_cache is None or "xt" not in _health_cache:
                source.health_check()
                if _health_cache is not None:
                    _health_cache["xt"] = True

            return type(
                "Observation",
                (),
                {
                    "source_status": "HEALTHY",
                    "price": 65000.0,
                    "source": "xt",
                    "fallback_used": False,
                },
            )()

    class FakeSourceCandlePipeline:
        def fetch_and_store(
            self,
            symbol,
            timeframe,
            _health_cache=None,
        ):
            if _health_cache is None or "xt" not in _health_cache:
                source.health_check()
                if _health_cache is not None:
                    _health_cache["xt"] = True

            return {
                "stored": True,
                "source": "xt",
                "candle": object(),
            }

    runtime = OperationalMarketContextRuntime(
        observer=FakeObserver(),
        market_data_pipeline=object(),
        database=database,
        source_candle_pipeline=FakeSourceCandlePipeline(),
    )

    runtime.context_pipeline.build = (
        lambda symbol, timeframes=None: OperationalMarketContext(
            symbol=symbol,
            trend="NEUTRAL",
            signal="WAIT",
            confidence=50.0,
            timestamp="test",
        )
    )

    result = runtime.run_cycle(
        symbol="BTCUSDT",
        timeframes=("5m", "15m", "30m", "4H", "1D"),
    )

    assert result["context"] is not None

    # One source health check per operational cycle.
    assert source.health_check_calls == 1

    database.close()
