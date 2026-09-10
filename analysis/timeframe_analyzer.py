from analysis.market_analyzer import MarketAnalyzer
from analysis.timeframe import TimeframeAnalysis


class TimeframeAnalyzer:

    def __init__(self):

        self.market_analyzer = MarketAnalyzer()

    def analyze(self, prices, timeframe):

        result = self.market_analyzer.analyze(prices)

        signals = result["signals"]

        trend = "NEUTRAL"
        signal = "WAIT"

        if "Bullish Trend" in signals:
            trend = "BULLISH"

        elif "Bearish Trend" in signals:
            trend = "BEARISH"

        has_positive_momentum = (
            "Positive Momentum" in signals
        )

        has_negative_momentum = (
            "Negative Momentum" in signals
        )

        if trend == "BULLISH" and has_positive_momentum:
            signal = "BUY"

        elif trend == "BEARISH" and has_negative_momentum:
            signal = "SELL"

        confidence = result["confidence"]["confidence"]

        return TimeframeAnalysis(
            timeframe=timeframe,
            trend=trend,
            signal=signal,
            confidence=confidence
        )