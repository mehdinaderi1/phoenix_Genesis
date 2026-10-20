import os

from analysis.market_analyzer import MarketAnalyzer
from analysis.timeframe import TimeframeAnalysis


class TimeframeAnalyzer:
    """
    Analyzes one timeframe and produces a directional signal.

    Two modes:
    - Legacy (default): requires trend AND momentum aligned
    - Trend-first: accepts trend direction even if momentum disagrees
      (pullback-friendly), activated via PHOENIX_TREND_FIRST=1

    Confidence is inverted for SELL signals when
    PHOENIX_SYMMETRIC_CONFIDENCE=1 (ConfidenceEngine is bullish-biased).
    """

    USE_TREND_FIRST = (
        os.getenv("PHOENIX_TREND_FIRST", "0").strip() == "1"
    )

    USE_SYMMETRIC_CONFIDENCE = (
        os.getenv("PHOENIX_SYMMETRIC_CONFIDENCE", "0").strip() == "1"
    )

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

        if self.USE_TREND_FIRST:
            if trend == "BULLISH":
                signal = "BUY"
            elif trend == "BEARISH":
                signal = "SELL"
        else:
            if trend == "BULLISH" and has_positive_momentum:
                signal = "BUY"
            elif trend == "BEARISH" and has_negative_momentum:
                signal = "SELL"

        confidence = result["confidence"]["confidence"]

        if self.USE_SYMMETRIC_CONFIDENCE and signal == "SELL":
            confidence = 100.0 - confidence

        return TimeframeAnalysis(
            timeframe=timeframe,
            trend=trend,
            signal=signal,
            confidence=confidence,
            reasons=tuple(signals),
        )