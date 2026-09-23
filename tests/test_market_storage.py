from core.database import DatabaseManager
from core.market_data.repository import MarketDataRepository


def test_market_data_storage(tmp_path):
    database = DatabaseManager(str(tmp_path / "test.db"))
    database.connect()

    repository = MarketDataRepository(database)

    saved = repository.save_candle(
        "BTCUSDT", "30m", 65000, 65100, 64900, 65000, 120, 123456789
    )

    assert saved is True

    data = repository.get_latest_candles("BTCUSDT")

    assert len(data) == 1
    assert data[0][1] == "BTCUSDT"
    assert data[0][2] == "30m"
    assert data[0][3] == 123456789
    assert data[0][7] == 65000

    database.close()


def test_get_latest_candle_is_scoped_by_timeframe_and_timestamp(tmp_path):
    database = DatabaseManager(str(tmp_path / "test.db"))
    database.connect()

    repository = MarketDataRepository(database)

    repository.save_candle("BTCUSDT", "5m", 100, 110, 90, 105, 10, 300)
    repository.save_candle("BTCUSDT", "5m", 105, 115, 95, 110, 11, 600)
    repository.save_candle("BTCUSDT", "15m", 200, 210, 190, 205, 20, 900)

    candle = repository.get_latest_candle("BTCUSDT", "5m")

    assert candle[1] == "BTCUSDT"
    assert candle[2] == "5m"
    assert candle[3] == 600
    assert candle[7] == 110

    database.close()


def test_get_latest_candle_returns_none_when_missing(tmp_path):
    database = DatabaseManager(str(tmp_path / "test.db"))
    database.connect()

    repository = MarketDataRepository(database)

    assert repository.get_latest_candle("BTCUSDT", "5m") is None

    database.close()
