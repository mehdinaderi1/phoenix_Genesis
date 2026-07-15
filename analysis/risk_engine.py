class RiskEngine:

    def analyze(self, confidence, signals):

        if isinstance(confidence, dict):
            confidence_score = confidence["confidence"]
        else:
            confidence_score = confidence

        risk_level = "Medium"
        warnings = []

        if confidence_score >= 80:
            risk_level = "Low"

        elif confidence_score < 50:
            risk_level = "High"

        if "Overbought" in signals:
            warnings.append("Market may be overheated")

        if "Bearish Trend" in signals:
            warnings.append("Bearish trend detected")

        return {
            "risk": risk_level,
            "warnings": warnings
        }