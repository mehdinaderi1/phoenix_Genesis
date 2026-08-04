class ReasoningEngine:

    def __init__(self):
        pass


    def analyze(self, analysis_data):

        class Consensus:
            pass


        consensus = Consensus()

        original_trend = analysis_data.get(
            "trend",
            "Unknown"
        )

        consensus.trend = original_trend.upper()

        consensus.confidence = analysis_data.get(
            "confidence",
            0
        )

        consensus.signal = analysis_data.get(
            "signal",
            "WAIT"
        )


        reasons = []


        if consensus.trend == "BULLISH":
            reasons.append(
                "Market trend is bullish"
            )

        elif consensus.trend == "BEARISH":
            reasons.append(
                "Market trend is bearish"
            )

        else:
            reasons.append(
                "Market trend is unclear"
            )


        if analysis_data.get("momentum") == "Positive":
            reasons.append(
                "Momentum supports current trend"
            )


        return {
            "reasoning": " ".join(reasons),

            "trend": original_trend,

            "momentum": analysis_data.get(
                "momentum",
                "Unknown"
            )
        }