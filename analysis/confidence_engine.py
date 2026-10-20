import os


class ConfidenceEngine:
    """
    Confidence scoring engine with feature flag support.
    """

    USE_NEW_SCORING = (
        os.getenv("PHOENIX_NEW_CONFIDENCE", "0").strip() == "1"
    )

    LEGACY_BASE = 50
    LEGACY_WEIGHTS = {
        "Bullish Trend": 15,
        "Positive Momentum": 15,
        "Overbought": -10,
        "Bearish Trend": -15,
        "Negative Momentum": -15,
    }

    NEW_BASE = 60
    NEW_WEIGHTS = {
        "Bullish Trend": 20,
        "Positive Momentum": 20,
        "Overbought": -10,
        "Bearish Trend": -20,
        "Negative Momentum": -20,
    }

    def calculate(self, signals):

        if self.USE_NEW_SCORING:
            score = self.NEW_BASE
            weights = self.NEW_WEIGHTS
        else:
            score = self.LEGACY_BASE
            weights = self.LEGACY_WEIGHTS

        factors = {}

        for signal in signals:

            delta = weights.get(signal)

            if delta is None:
                continue

            score += delta
            factors[signal] = delta

        if score > 100:
            score = 100

        if score < 0:
            score = 0

        return {
            "confidence": score,
            "factors": factors
        }