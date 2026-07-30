from intelligence.governance.governance_memory import (
    GovernanceMemory
)

from intelligence.governance.governance_record import (
    GovernanceRecord
)

from intelligence.governance.governance_feedback import (
    GovernanceFeedback
)



def test_governance_feedback_success():


    memory = GovernanceMemory()


    strategy = {
        "name": "momentum_v2",
        "risk": "LOW"
    }


    memory.store(
        GovernanceRecord(
            strategy=strategy,
            status="APPROVED",
            reason="low risk"
        )
    )


    feedback = GovernanceFeedback(
        memory
    )


    result = feedback.evaluate(
        strategy,
        "SUCCESS"
    )


    assert result["status"] == "CONFIRMED"



def test_governance_feedback_failure():


    memory = GovernanceMemory()


    strategy = {
        "name": "high_risk",
        "risk": "HIGH"
    }


    memory.store(
        GovernanceRecord(
            strategy=strategy,
            status="APPROVED",
            reason="reviewed"
        )
    )


    feedback = GovernanceFeedback(
        memory
    )


    result = feedback.evaluate(
        strategy,
        "FAILURE"
    )


    assert result["status"] == "INCORRECT"