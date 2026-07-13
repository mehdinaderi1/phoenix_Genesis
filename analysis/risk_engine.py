class RiskEngine:

    def analyze(self, confidence, signals):

        risk_level = "Medium"
        warnings = []

        if confidence >= 80:
            risk_level = "Low"

        elif confidence < 50:
            risk_level = "High"


        if "Overbought" in signals:
            warnings.append("Market may be overheated")


        if "Bearish Trend" in signals:
            warnings.append("Bearish trend detected")


        return {
            "risk": risk_level,
            "warnings": warnings
        }