from market.candle import Candle


class MarketDataEngine:

    def __init__(self, exchange, database):

        self.exchange = exchange
        self.database = database


    def get_price(self, symbol):

        return self.exchange.get_price(symbol)


    def get_candle(self, symbol, timeframe="1m"):

        data = self.exchange.get_candle(symbol)

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

        if self.database:
            self.database.insert_candle(candle)

        return candle