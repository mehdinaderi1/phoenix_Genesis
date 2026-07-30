from intelligence.governance.governance_confidence import (
    GovernanceConfidence
)


def test_intelligence_governance_flow_confirmed():

    base_confidence = 70


    governance = GovernanceConfidence()


    governance_score = governance.calculate(
        {
            "status": "CONFIRMED"
        }
    )


    final_confidence = (
        base_confidence
        +
        governance_score
    )


    decision = {
        "action": "LONG",
        "confidence": final_confidence
    }


    assert governance_score == 10
    assert decision["confidence"] == 80
    assert decision["action"] == "LONG"



def test_intelligence_governance_flow_rejected():

    base_confidence = 70


    governance = GovernanceConfidence()


    governance.calculate(
        {
            "status": "CONFIRMED"
        }
    )


    governance_score = governance.calculate(
        {
            "status": "INCORRECT"
        }
    )


    final_confidence = (
        base_confidence
        +
        governance_score
    )


    decision = {
        "action": "WAIT",
        "confidence": final_confidence
    }


    assert governance_score == 0
    assert decision["confidence"] == 70
    assert decision["action"] == "WAIT"