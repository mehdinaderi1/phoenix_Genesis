class DecisionEngine:

    def decide(self, confidence, signals):

        decision = "WAIT"

        risk = "Medium"

        if confidence >= 80:
            decision = "STRONG SIGNAL"
            risk = "Low"

        elif confidence >= 60:
            decision = "WATCH"

        elif confidence < 40:
            decision = "IGNORE"
            risk = "High"


        if "Bearish Trend" in signals:
            decision = "AVOID"

        return {
            "decision": decision,
            "confidence": confidence,
            "risk": risk
        }