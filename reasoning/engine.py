class ReasoningEngine:

    def analyze(self, analysis_data):

        trend = analysis_data.get("trend", "Unknown")
        momentum = analysis_data.get("momentum", "Unknown")

        if trend == "Bullish" and momentum == "Positive":
            message = "Market structure is showing bullish confirmation."

        elif trend == "Bearish":
            message = "Market structure indicates downside pressure."

        else:
            message = "Market conditions are unclear. Monitoring required."

        return {
            "reasoning": message,
            "trend": trend,
            "momentum": momentum
        }