class ConfidenceEngine:

    def calculate(self, factors):

        score = 0

        technical = factors.get("technical", 0)
        timeframe = factors.get("timeframe", 0)
        regime = factors.get("regime", 0)
        risk = factors.get("risk", 0)

        score += technical
        score += timeframe
        score += regime
        score += risk

        if score > 100:
            score = 100

        if score < 0:
            score = 0

        return {
            "confidence": score,
            "components": {
                "technical": technical,
                "timeframe": timeframe,
                "regime": regime,
                "risk": risk
            }
        }