class ReasoningEngine:

    def generate(self, consensus, risk_assessment=None):

        reasons = []

        if consensus.signal == "BUY":
            reasons.append(
                "Positive market consensus"
            )

        elif consensus.signal == "SELL":
            reasons.append(
                "Negative market consensus"
            )

        if consensus.trend == "BULLISH":
            reasons.append(
                "Bullish trend confirmed"
            )

        elif consensus.trend == "BEARISH":
            reasons.append(
                "Bearish trend detected"
            )

        if consensus.confidence >= 80:
            reasons.append(
                "High confidence score"
            )

        elif consensus.confidence < 50:
            reasons.append(
                "Low confidence score"
            )

        if consensus.signal == "WAIT":
            reasons.append(
                "Timeframe conflict detected"
            )


        if consensus.confidence >= 75:
            risk_level = "LOW"

        elif consensus.confidence >= 50:
            risk_level = "MEDIUM"

        else:
            risk_level = "HIGH"


        if risk_assessment:

            risk_level = risk_assessment.level

            for reason in risk_assessment.reasons:
                reasons.append(reason)


        return {
            "signal": consensus.signal,
            "confidence": consensus.confidence,
            "risk": risk_level,
            "reasons": reasons
        }