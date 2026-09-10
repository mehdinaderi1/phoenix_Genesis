from analysis.timeframe_analyzer import TimeframeAnalyzer
from intelligence.multitimeframe import MultiTimeframeAnalyzer
from market.market_data_reader import MarketDataReader


class MultiTimeframePipeline:

    def __init__(self, database):

        self.reader = MarketDataReader(database)
        self.timeframe_analyzer = TimeframeAnalyzer()
        self.consensus_analyzer = MultiTimeframeAnalyzer()

    def analyze(self, symbol="BTCUSDT"):

        timeframe_analyses = []

        for timeframe in ("30m", "4H", "1D"):

            prices = self.reader.get_close_prices(
                symbol,
                timeframe
            )

            if not prices:
                continue

            analysis = self.timeframe_analyzer.analyze(
                prices,
                timeframe
            )

            timeframe_analyses.append(
                analysis
            )

        return self.consensus_analyzer.analyze(
            timeframe_analyses
        )