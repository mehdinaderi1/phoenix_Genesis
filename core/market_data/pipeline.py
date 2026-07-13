from core.market_data.repository import MarketDataRepository


class MarketDataPipeline:

    def __init__(self, exchange, database):
        self.exchange = exchange
        self.repository = MarketDataRepository(database)


    def fetch_and_store(
        self,
        symbol="BTCUSDT",
        timeframe="1m"
    ):

        candle = self.exchange.get_candle(
            symbol,
            timeframe
        )

        self.repository.save_candle(
            symbol,
            timeframe,
            candle["open"],
            candle["high"],
            candle["low"],
            candle["close"],
            candle["volume"],
            candle["timestamp"]
        )


        return candle