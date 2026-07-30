from intelligence.governance.governance_gate import (
    GovernanceGate
)



def test_governance_gate_accept():

    gate = GovernanceGate()


    result = gate.evaluate(
        {
            "status": "APPROVED",
            "confidence": 10
        }
    )


    assert result["approved"] is True



def test_governance_gate_reject():

    gate = GovernanceGate()


    result = gate.evaluate(
        {
            "status": "REJECTED",
            "confidence": 10
        }
    )


    assert result["approved"] is False



def test_governance_gate_low_confidence():

    gate = GovernanceGate(
        minimum_confidence=5
    )


    result = gate.evaluate(
        {
            "status": "APPROVED",
            "confidence": 0
        }
    )


    assert result["approved"] is False