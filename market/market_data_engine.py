from market.candle import Candle
from core.market_data.pipeline import MarketDataPipeline


class MarketDataEngine:

    def __init__(self, exchange, database):

        self.exchange = exchange
        self.database = database
        self.pipeline = MarketDataPipeline(
            exchange,
            database
        )


    def get_price(self, symbol):

        return self.exchange.get_price(symbol)


    def get_candle(self, symbol, timeframe="1m"):

        data = self.pipeline.fetch_and_store(
            symbol,
            timeframe
        )


        if data is None:
            return None


        candle = Candle(
            symbol=symbol,
            timeframe=timeframe,
            timestamp=data["timestamp"],
            open=data["open"],
            high=data["high"],
            low=data["low"],
            close=data["close"],
            volume=data["volume"]
        )


        return candle