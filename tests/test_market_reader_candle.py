from core.database import DatabaseManager
from market.market_data_reader import MarketDataReader
from market.candle import Candle


def test_reader_returns_candle():

    db = DatabaseManager()

    db.connect()
    db.create_tables()


    reader = MarketDataReader(db)


    candle = reader.get_latest_candle("BTCUSDT")


    if candle:

        assert isinstance(candle, Candle)

        assert candle.symbol == "BTCUSDT"

        assert candle.close > 0

        print("✅ Reader Candle Object Test Passed")


    else:

        print("⚠️ No candle data found")


    db.close()



if __name__ == "__main__":

    test_reader_returns_candle()