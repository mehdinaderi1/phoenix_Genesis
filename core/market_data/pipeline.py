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

        if candle is None:
            return None


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



    def fetch_multi_timeframes(
        self,
        symbol="BTCUSDT",
        timeframes=None
    ):

        if timeframes is None:
            timeframes = [
                "1m",
                "30m",
                "4H",
                "1D"
            ]


        results = {}


        for timeframe in timeframes:

            candle = self.fetch_and_store(
                symbol,
                timeframe
            )

            results[timeframe] = candle


        return results

    def fetch_and_store_historical(
        self,
        symbol="BTCUSDT",
        timeframe="1m",
        limit=30
    ):

        candles = self.exchange.get_historical_candles(
            symbol,
            timeframe,
            limit
        )

        if not candles:
            return []

        stored = []

        for candle in candles:

            saved = self.repository.save_candle(
                symbol,
                timeframe,
                candle["open"],
                candle["high"],
                candle["low"],
                candle["close"],
                candle["volume"],
                candle["timestamp"]
            )

            if saved:
                stored.append(candle)

        return stored