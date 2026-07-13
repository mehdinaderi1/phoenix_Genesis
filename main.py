from core.engine import PhoenixEngine
from exchanges.exchange_manager import ExchangeManager
from exchanges.mock_exchange import MockExchange
from market.market_data_engine import MarketDataEngine
from market.market_data_reader import MarketDataReader
from core.market_data.pipeline import MarketDataPipeline


def main():

    print("🦅 Phoenix Genesis Starting...")

    engine = PhoenixEngine()
    engine.start()


    exchange_manager = ExchangeManager()

    mock = MockExchange()
    exchange_manager.set_exchange(mock)


    print(exchange_manager.connect())


    price = exchange_manager.get_price("BTCUSDT")
    print(f"BTC Price: {price}")


    balance = exchange_manager.get_balance()
    print(f"Balance: {balance}")


    pipeline = MarketDataPipeline(
    exchange_manager,
    engine.database
    )


    multi_data = pipeline.fetch_multi_timeframes(
        "BTCUSDT"
    )


    print("==============================")
    print("🦅 Phoenix Multi Timeframe Data")
    print("==============================")


    for timeframe, candle in multi_data.items():

        print(f"\nTimeframe: {timeframe}")

        if candle:
            print("Close:", candle["close"])
            print("Volume:", candle["volume"])


    market_engine = MarketDataEngine(
        exchange_manager,
        engine.database
    )


    candle = market_engine.get_candle("BTCUSDT")


    print("==============================")
    print("🦅 Phoenix Market Data")
    print("==============================")

    print(candle)
    print("Close Price:", candle.close)
    print("Volume:", candle.volume)



    reader = MarketDataReader(
        engine.database
    )


    latest = reader.get_latest_candle(
        "BTCUSDT"
    )


    print("==============================")
    print("🦅 Latest Phoenix Candle")
    print("==============================")

    print(latest)



    candles = engine.database.get_candles()


    print("==============================")
    print("🦅 Stored Market Candles")
    print("==============================")


    for item in candles:
        print(item)



if __name__ == "__main__":
    main()