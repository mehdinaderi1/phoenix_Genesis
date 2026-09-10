from core.database import DatabaseManager
from core.market_data.repository import MarketDataRepository


def test_market_data_storage(tmp_path):

    database = DatabaseManager(
        str(tmp_path / "test.db")
    )

    database.connect()

    repository = MarketDataRepository(database)

    saved = repository.save_candle(
        "BTCUSDT",
        "30m",
        65000,
        65100,
        64900,
        65000,
        120,
        123456789
    )

    assert saved is True

    data = repository.get_latest_candles(
        "BTCUSDT"
    )

    assert len(data) == 1
    assert data[0][1] == "BTCUSDT"
    assert data[0][2] == "30m"
    assert data[0][3] == 123456789
    assert data[0][7] == 65000

    database.close()