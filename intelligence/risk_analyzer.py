from intelligence.risk_assessment import RiskAssessment


class RiskAnalyzer:

    def analyze(self, consensus):

        confidence = consensus.confidence

        if confidence >= 80:
            return RiskAssessment(
                level="LOW",
                score=confidence,
                reasons=[
                    "High confidence consensus"
                ]
            )

        elif confidence >= 60:
            return RiskAssessment(
                level="MEDIUM",
                score=confidence,
                reasons=[
                    "Moderate confidence consensus"
                ]
            )

        else:
            return RiskAssessment(
                level="HIGH",
                score=confidence,
                reasons=[
                    "Low confidence consensus"
                ]
            )