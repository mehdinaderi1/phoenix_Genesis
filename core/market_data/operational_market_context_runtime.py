from core.market_data.observation_market_data import ObservationMarketDataBridge
from core.market_data.operational_market_context_pipeline import OperationalMarketContextPipeline


class OperationalMarketContextRuntime:

    def __init__(
        self,
        observer=None,
        market_data_pipeline=None,
        database=None,
        validation_pipeline=None,
        validated_context_pipeline=None,
        source_candle_pipeline=None
    ):
        if database is None:
            if observer is not None and market_data_pipeline is None:
                database = observer
                observer = None
            else:
                raise ValueError("database must not be None")

        self.observer = None
        self.market_data_bridge = None

        if observer is not None and market_data_pipeline is not None:
            self.observer = observer
            self.market_data_bridge = ObservationMarketDataBridge(
                observer,
                market_data_pipeline
            )

        self.source_candle_pipeline = source_candle_pipeline

        self.context_pipeline = OperationalMarketContextPipeline(database)
        self.validation_pipeline = validation_pipeline
        self.validated_context_pipeline = validated_context_pipeline

    def run_cycle(self, symbol="BTCUSDT", timeframes=None):

        if timeframes is None:
            timeframes = ("30m", "4H", "1D")

        observation = None

        if self.observer is not None:
            observation = self.observer.observe(symbol)

            if observation.source_status == "BLIND":
                return {
                    "observation": observation,
                    "context": None
                }

        stored = False

        if self.source_candle_pipeline is not None:

            for timeframe in timeframes:
                result = self.source_candle_pipeline.fetch_and_store(
                    symbol=symbol,
                    timeframe=timeframe
                )

                if result.get("stored"):
                    stored = True

        elif self.market_data_bridge is not None:

            for timeframe in timeframes:
                candle = (
                    self.market_data_bridge
                    .market_data_pipeline
                    .fetch_and_store(
                        symbol=symbol,
                        timeframe=timeframe
                    )
                )

                if candle is not None:
                    stored = True

        if (
            self.observer is not None
            or self.source_candle_pipeline is not None
            or self.market_data_bridge is not None
        ):
            if not stored:
                return {
                    "observation": observation,
                    "context": None
                }

        if self.validated_context_pipeline is not None:

            validated_result = self.validated_context_pipeline.build(
                symbol
            )

            return {
                "observation": observation,
                "validation": validated_result["validation"],
                "context": validated_result["context"]
            }

        if self.validation_pipeline is not None:

            validation = self.validation_pipeline.validate(symbol)

            if validation.status not in {"VALID", "INSUFFICIENT"}:
                return {
                    "observation": observation,
                    "validation": validation,
                    "context": None
                }

        else:
            validation = None

        context = self.context_pipeline.build(symbol)

        return {
            "observation": observation,
            "validation": validation,
            "context": context
        }

    def run(
        self,
        symbol="BTCUSDT",
        cycles=1,
        timeframes=None
    ):

        if cycles <= 0:
            raise ValueError(
                "cycles must be greater than zero"
            )

        contexts = []

        for _ in range(cycles):

            result = self.run_cycle(
                symbol=symbol,
                timeframes=timeframes
            )

            context = result["context"]

            if context is None:
                continue

            contexts.append(context)
            self._print_context(context)

        return contexts

    def _print_context(self, context):

        print(
            f"[MARKET] {context.symbol} | "
            f"trend={context.trend} | "
            f"signal={context.signal} | "
            f"confidence={context.confidence}"
        )
