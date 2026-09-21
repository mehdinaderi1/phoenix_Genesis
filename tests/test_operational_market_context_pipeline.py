from core.database import DatabaseManager
from core.market_data.operational_market_context import OperationalMarketContext
from core.market_data.operational_market_context_pipeline import OperationalMarketContextPipeline


def test_operational_market_context_pipeline_reads_mtf(tmp_path):
    database = DatabaseManager(db_path=str(tmp_path / "phoenix.db"))
    database.connect()

    for timeframe in ("30m", "4H", "1D"):
        for index, price in enumerate([65000.0] * 5):
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

    pipeline = OperationalMarketContextPipeline(database)
    context = pipeline.build("BTCUSDT")

    assert isinstance(context, OperationalMarketContext)
    assert context.symbol == "BTCUSDT"
    assert context.trend == "NEUTRAL"
    assert context.signal == "WAIT"
    assert context.confidence == 50.0
    assert context.timestamp

    database.close()

def test_operational_market_context_pipeline_accepts_custom_timeframes(
    tmp_path
):
    database = DatabaseManager(
        db_path=str(tmp_path / "custom_timeframes.db")
    )
    database.connect()

    timeframes = (
        "5m",
        "15m",
        "30m",
        "4H",
        "1D"
    )

    prices = [
        64000.0,
        64200.0,
        64500.0,
        64800.0,
        65000.0,
        65200.0,
        65500.0,
        65800.0,
        66000.0,
        66300.0,
        66500.0,
        66800.0,
        67000.0,
        67200.0,
        67500.0,
        67800.0,
        68000.0,
        68300.0,
        68500.0,
        68800.0,
        69000.0,
        69300.0,
        69500.0,
        69800.0,
        70000.0,
        70200.0,
        70500.0,
        70800.0,
        71000.0,
        71200.0
    ]

    for timeframe in timeframes:
        for index, price in enumerate(prices):
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

    pipeline = OperationalMarketContextPipeline(database)

    context = pipeline.build(
        "BTCUSDT",
        timeframes=timeframes
    )

    assert isinstance(context, OperationalMarketContext)
    assert context.symbol == "BTCUSDT"
    assert context.trend == "BULLISH"
    assert context.signal == "BUY"
    assert 0 <= context.confidence <= 100
    assert context.timestamp

    database.close()
