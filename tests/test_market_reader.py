from core.database import DatabaseManager
from market.market_data_reader import MarketDataReader


def test():

    db = DatabaseManager()
    db.connect()

    reader = MarketDataReader(db)

    prices = reader.get_close_prices("BTCUSDT")

    print(prices)

    print("✅ Market Reader Passed")


if __name__ == "__main__":
    test()