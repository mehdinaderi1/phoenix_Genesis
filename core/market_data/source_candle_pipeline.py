from core.market_data.repository import MarketDataRepository


class SourceCandlePipeline:
    """Fetches candles through the market-data source manager and stores them."""

    def __init__(self, source_manager, database):
        if source_manager is None:
            raise ValueError("source_manager must not be None")
        if database is None:
            raise ValueError("database must not be None")

        self.source_manager = source_manager
        self.repository = MarketDataRepository(database)

    def fetch_and_store(self, symbol="BTCUSDT", timeframe="1m"):
        if not symbol:
            raise ValueError("symbol must not be empty")

        ordered_names = []
        if self.source_manager.primary_source:
            ordered_names.append(self.source_manager.primary_source)

        ordered_names.extend(
            name
            for name in self.source_manager.sources
            if name != self.source_manager.primary_source
        )

        for name in ordered_names:
            source = self.source_manager.sources[name]

            try:
                if not source.health_check():
                    continue
                candle = source.get_candle(symbol, timeframe)
            except Exception:
                continue

            if candle is None:
                continue

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

            return {
                "stored": bool(saved),
                "source": name,
                "candle": candle
            }

        return {
            "stored": False,
            "source": None,
            "candle": None
        }
