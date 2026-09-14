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
