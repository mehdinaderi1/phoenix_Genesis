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
