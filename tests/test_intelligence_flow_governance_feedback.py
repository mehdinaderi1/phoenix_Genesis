from intelligence.flow import IntelligenceFlow



def test_governance_feedback_update():

    flow = IntelligenceFlow()


    strategy = {
        "name": "momentum_v2",
        "risk": "LOW"
    }


    result = flow.update_governance_feedback(
        strategy,
        "SUCCESS"
    )


    assert result["feedback"]["status"] in [
        "CONFIRMED",
        "UNKNOWN"
    ]


    assert "confidence" in result