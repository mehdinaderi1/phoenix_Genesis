from core.market_data.observer import RealMarketObserver


class ObservationMarketDataBridge:
    def __init__(self, observer, market_data_pipeline):
        if observer is None:
            raise ValueError("observer must not be None")
        if market_data_pipeline is None:
            raise ValueError("market_data_pipeline must not be None")

        self.observer = observer
        self.market_data_pipeline = market_data_pipeline

    def observe_and_store(self, symbol="BTCUSDT", timeframe="1m"):
        observation = self.observer.observe(symbol)

        if observation.source_status == "BLIND":
            return {
                "observation": observation,
                "candle": None,
                "stored": False
            }

        candle = self.market_data_pipeline.fetch_and_store(
            symbol=symbol,
            timeframe=timeframe
        )

        return {
            "observation": observation,
            "candle": candle,
            "stored": candle is not None
        }
