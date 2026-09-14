from core.market_data.observation_market_data import ObservationMarketDataBridge
from core.market_data.operational_market_context_pipeline import OperationalMarketContextPipeline


class OperationalMarketContextRuntime:
    def __init__(self, observer=None, market_data_pipeline=None, database=None):
        if database is None:
            if observer is not None and market_data_pipeline is None:
                database = observer
                observer = None
            else:
                raise ValueError("database must not be None")

        if observer is None or market_data_pipeline is None:
            self.observer = None
            self.market_data_bridge = None
        else:
            self.observer = observer
            self.market_data_bridge = ObservationMarketDataBridge(
                observer,
                market_data_pipeline
            )

        self.context_pipeline = OperationalMarketContextPipeline(database)

    def run(self, symbol="BTCUSDT", cycles=1, timeframes=None):
        if cycles <= 0:
            raise ValueError("cycles must be greater than zero")

        if timeframes is None:
            timeframes = ("30m", "4H", "1D")

        contexts = []

        for _ in range(cycles):
            if self.market_data_bridge is not None:
                observation = self.observer.observe(symbol)

                if observation.source_status == "BLIND":
                    continue

                stored = False

                for timeframe in timeframes:
                    candle = self.market_data_bridge.market_data_pipeline.fetch_and_store(
                        symbol=symbol,
                        timeframe=timeframe
                    )
                    if candle is not None:
                        stored = True

                if not stored:
                    continue

            context = self.context_pipeline.build(symbol)
            contexts.append(context)
            self._print_context(context)

        return contexts

    @staticmethod
    def _print_context(context):
        print(
            f"[MARKET] {context.symbol} "
            f"trend={context.trend} "
            f"signal={context.signal} "
            f"confidence={context.confidence:.2f}% "
            f"timestamp={context.timestamp}"
        )
