from core.database import DatabaseManager
from core.market_data.operational_market_context_runtime import (
    OperationalMarketContextRuntime
)


def test_runtime_builds_timeframe_candle_boundaries(tmp_path):
    database = DatabaseManager(str(tmp_path / "test.db"))
    database.connect()

    database.connection.execute(
        """
        INSERT INTO market_candles
        (symbol, timeframe, open, high, low, close, volume, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        ("BTCUSDT", "5m", 100, 110, 90, 105, 10, 1790111100)
    )

    database.connection.commit()

    runtime = OperationalMarketContextRuntime(
        database=database
    )

    result = runtime._build_candle_boundaries(
        "BTCUSDT",
        ("5m",),
        now=1790111200
    )

    boundary = result["5m"]

    assert boundary["timeframe"] == "5m"
    assert boundary["candle_start"] == 1790111100
    assert boundary["next_boundary"] == 1790111400
    assert boundary["duration_seconds"] == 300
    assert boundary["age_seconds"] == 100
    assert boundary["is_closed"] is False

    database.close()


def test_runtime_returns_none_boundary_when_candle_missing(tmp_path):
    database = DatabaseManager(str(tmp_path / "test.db"))
    database.connect()

    runtime = OperationalMarketContextRuntime(
        database=database
    )

    result = runtime._build_candle_boundaries(
        "BTCUSDT",
        ("5m",),
        now=1790111200
    )

    assert result["5m"] is None

    database.close()
