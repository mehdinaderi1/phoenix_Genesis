from intelligence.governance.governance_confidence import (
    GovernanceConfidence
)


def test_governance_confidence_flow_confirmed():

    governance = GovernanceConfidence()


    result = governance.calculate(
        {
            "status": "CONFIRMED"
        }
    )


    adjusted_confidence = 70 + result


    assert result == 10
    assert adjusted_confidence == 80



def test_governance_confidence_flow_incorrect():

    governance = GovernanceConfidence()


    governance.calculate(
        {
            "status": "CONFIRMED"
        }
    )


    result = governance.calculate(
        {
            "status": "INCORRECT"
        }
    )


    adjusted_confidence = 70 + result


    assert result == 0
    assert adjusted_confidence == 70