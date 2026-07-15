from intelligence.regime import MarketRegime


class RegimeAnalyzer:

    def analyze(self, consensus):

        if (
            consensus.trend == "BULLISH"
            and consensus.signal == "BUY"
            and consensus.confidence >= 75
        ):
            return MarketRegime(
                regime="TRENDING_BULLISH",
                confidence=consensus.confidence,
                reasons=[
                    "Bullish consensus",
                    "High confidence signal"
                ]
            )

        if (
            consensus.trend == "BEARISH"
            and consensus.signal == "SELL"
            and consensus.confidence >= 75
        ):
            return MarketRegime(
                regime="TRENDING_BEARISH",
                confidence=consensus.confidence,
                reasons=[
                    "Bearish consensus",
                    "High confidence signal"
                ]
            )

        return MarketRegime(
            regime="RANGING",
            confidence=consensus.confidence,
            reasons=[
                "Weak market direction",
                "Insufficient trend confidence"
            ]
        )