import sys
import os

sys.path.insert(
    0,
    os.path.dirname(
        os.path.dirname(__file__)
    )
)

from exchanges.mock_exchange import MockExchange

from core.database import DatabaseManager

from market.market_data_engine import MarketDataEngine

from market.market_data_reader import MarketDataReader



def test_market_data_pipeline():

    print("\n🦅 Testing Phoenix Market Data Pipeline")


    # Database
    database = DatabaseManager()
    database.connect()


    # Exchange
    exchange = MockExchange()
    print(exchange.connect())


    # Market Engine
    engine = MarketDataEngine(
        exchange,
        database
    )


    # دریافت و ذخیره Candle
    candle = engine.get_candle("BTCUSDT")


    assert candle.symbol == "BTCUSDT"
    assert candle.close > 0


    print("✅ Candle Created")


    # Reader
    reader = MarketDataReader(database)


    latest = reader.get_latest_candle(
        "BTCUSDT"
    )


    assert latest is not None


    print("✅ Candle Stored")


    database.close()



if __name__ == "__main__":

    test_market_data_pipeline()