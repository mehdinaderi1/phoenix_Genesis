import os

from intelligence.risk_assessment import RiskAssessment


class RiskAnalyzer:

    USE_RELAXED_RISK = (
        os.getenv("PHOENIX_RELAXED_RISK", "0").strip() == "1"
    )

    def analyze(self, consensus):

        confidence = consensus.confidence

        if self.USE_RELAXED_RISK:
            low_threshold = 60
            medium_threshold = 25
        else:
            low_threshold = 80
            medium_threshold = 60

        if confidence >= low_threshold:
            return RiskAssessment(
                level="LOW",
                score=confidence,
                reasons=["High confidence consensus"],
            )
        elif confidence >= medium_threshold:
            return RiskAssessment(
                level="MEDIUM",
                score=confidence,
                reasons=["Moderate confidence consensus"],
            )
        else:
            return RiskAssessment(
                level="HIGH",
                score=confidence,
                reasons=["Low confidence consensus"],
            )