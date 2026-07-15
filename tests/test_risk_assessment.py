from intelligence.risk_assessment import RiskAssessment


def test_risk_assessment():

    risk = RiskAssessment(
        level="LOW",
        score=85,
        reasons=[
            "High confidence"
        ]
    )

    assert risk.level == "LOW"
    assert risk.score == 85