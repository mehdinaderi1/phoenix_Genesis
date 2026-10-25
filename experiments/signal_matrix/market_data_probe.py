from experiments.signal_matrix.signal_matrix import (
    SignalMatrix,
    StrategySignal,
)
from experiments.signal_matrix.timeframe_adapter import (
    record_timeframe_analysis,
)


class MarketDataMatrixProbe:
    """Experimental per-timeframe reporting; never places orders."""

    def __init__(self, reader, analyzer):
        self.reader = reader
        self.analyzer = analyzer

    def run(self, symbol="BTCUSDT", timeframes=("5m", "15m", "30m", "4H", "1D")):
        matrix = SignalMatrix()

        for timeframe in timeframes:
            try:
                prices = self.reader.get_close_prices(symbol, timeframe)

                if not prices:
                    matrix.add(
                        StrategySignal(
                            strategy="TimeframeAnalyzer",
                            timeframe=timeframe,
                            state="DATA_ERROR",
                            reasons=("No close-price data available",),
                            data_valid=False,
                        )
                    )
                    continue

                analysis = self.analyzer.analyze(prices, timeframe)

                if analysis is None:
                    matrix.add(
                        StrategySignal(
                            strategy="TimeframeAnalyzer",
                            timeframe=timeframe,
                            state="DATA_ERROR",
                            reasons=("Analyzer returned no result",),
                            data_valid=False,
                        )
                    )
                    continue

                record_timeframe_analysis(
                    matrix=matrix,
                    strategy="TimeframeAnalyzer",
                    analysis=analysis,
                )

            except Exception as exc:
                matrix.add(
                    StrategySignal(
                        strategy="TimeframeAnalyzer",
                        timeframe=timeframe,
                        state="DATA_ERROR",
                        reasons=(f"{type(exc).__name__}: {exc}",),
                        data_valid=False,
                    )
                )

        return matrix
