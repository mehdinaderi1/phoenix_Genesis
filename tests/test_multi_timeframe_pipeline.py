from core.database import DatabaseManager
from market.candle import Candle
from analysis.multi_timeframe_pipeline import MultiTimeframePipeline


def test_multi_timeframe_pipeline(tmp_path):

    database = DatabaseManager(
        str(tmp_path / "test.db")
    )

    database.connect()

    prices = [
        64000,
        64200,
        64500,
        64800,
        65000,
        65200,
        65500,
        65800,
        66000,
        66300,
        66500,
        66800,
        67000,
        67200,
        67500,
        67800,
        68000,
        68300,
        68500,
        68800,
        69000,
        69300,
        69500,
        69800,
        70000,
        70200,
        70500,
        70800,
        71000,
        71200
    ]

    for index, timeframe in enumerate(
        ("30m", "4H", "1D")
    ):

        for price_index, price in enumerate(prices):

            candle = Candle(
                symbol="BTCUSDT",
                timeframe=timeframe,
                timestamp=index * 100000 + price_index,
                open=price,
                high=price,
                low=price,
                close=price,
                volume=100
            )

            database.insert_candle(candle)

    pipeline = MultiTimeframePipeline(
        database
    )

    result = pipeline.analyze(
        "BTCUSDT"
    )

    assert result is not None
    assert result.trend == "BULLISH"
    assert result.signal == "BUY"
    assert 0 <= result.confidence <= 100

    database.close()