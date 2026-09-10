from core.database import DatabaseManager
from core.market_data.pipeline import MarketDataPipeline
from exchanges.mock_exchange import MockExchange


def test_historical_market_data(tmp_path):

    database = DatabaseManager(
        str(tmp_path / "test.db")
    )

    database.connect()

    exchange = MockExchange()

    pipeline = MarketDataPipeline(
        exchange,
        database
    )

    candles = pipeline.fetch_and_store_historical(
        symbol="BTCUSDT",
        timeframe="30m",
        limit=30
    )

    assert len(candles) == 30

    stored = database.get_candles()

    assert len(stored) == 30

    assert stored[0][7] == 59300
    assert stored[-1][7] == 65100

    assert stored[0][3] < stored[-1][3]

    database.close()


def test_historical_market_data_duplicate_protection(tmp_path):

    database = DatabaseManager(
        str(tmp_path / "test.db")
    )

    database.connect()

    exchange = MockExchange()

    pipeline = MarketDataPipeline(
        exchange,
        database
    )

    first = pipeline.fetch_and_store_historical(
        symbol="BTCUSDT",
        timeframe="30m",
        limit=30
    )

    second = pipeline.fetch_and_store_historical(
        symbol="BTCUSDT",
        timeframe="30m",
        limit=30
    )

    assert len(first) == 30
    assert len(second) == 0

    stored = database.get_candles()

    assert len(stored) == 30

    database.close()