from intelligence.governance.governance_confidence import (
    GovernanceConfidence
)


def test_governance_confidence_increase():

    confidence = GovernanceConfidence()

    result = confidence.calculate(
        {
            "status": "CONFIRMED"
        }
    )

    assert result == 10



def test_governance_confidence_decrease():

    confidence = GovernanceConfidence()

    confidence.calculate(
        {
            "status": "CONFIRMED"
        }
    )

    result = confidence.calculate(
        {
            "status": "INCORRECT"
        }
    )

    assert result == 0