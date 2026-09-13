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

def test_multi_timeframe_pipeline_reacts_to_new_market_data(
    tmp_path
):

    database = DatabaseManager(
        str(tmp_path / "changing_market.db")
    )

    database.connect()

    pipeline = MultiTimeframePipeline(
        database
    )

    states = [
        [64000, 64200, 64500, 64800, 65000],
        [65000, 65500, 66000, 66500, 67000],
        [67000, 66500, 66000, 65500, 65000]
    ]

    results = []

    for state_index, prices in enumerate(states):

        for timeframe in ("30m", "4H", "1D"):

            for price_index, price in enumerate(prices):

                candle = Candle(
                    symbol="BTCUSDT",
                    timeframe=timeframe,
                    timestamp=(
                        state_index * 100000
                        + price_index
                    ),
                    open=price,
                    high=price,
                    low=price,
                    close=price,
                    volume=100
                )

                database.insert_candle(candle)

        result = pipeline.analyze(
            "BTCUSDT"
        )

        results.append(result)

    assert len(results) == 3

    assert all(
        result is not None
        for result in results
    )

    assert results[0].trend != results[2].trend

    database.close()

