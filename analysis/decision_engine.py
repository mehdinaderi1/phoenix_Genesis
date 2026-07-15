class DecisionEngine:

    def decide(self, confidence, signals):

        if isinstance(confidence, dict):
            confidence_score = confidence["confidence"]
        else:
            confidence_score = confidence

        decision = "WAIT"

        risk = "Medium"

        if confidence_score >= 80:
            decision = "STRONG SIGNAL"
            risk = "Low"

        elif confidence_score >= 60:
            decision = "WATCH"

        elif confidence_score < 40:
            decision = "IGNORE"
            risk = "High"

        if "Bearish Trend" in signals:
            decision = "AVOID"

        return {
            "decision": decision,
            "confidence": confidence_score,
            "risk": risk
        }