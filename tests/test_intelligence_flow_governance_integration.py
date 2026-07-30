from intelligence.flow import IntelligenceFlow
from intelligence.governance.governance_record import (
    GovernanceRecord
)


def test_intelligence_flow_governance_feedback_confirmed():

    flow = IntelligenceFlow()


    record = GovernanceRecord(
        strategy={
            "name": "strategy_alpha"
        },
        status="CONFIRMED",
        reason="valid strategy"
    )


    flow.governance_memory.store(
        record
    )


    result = flow.update_governance_feedback(
        {
            "name": "strategy_alpha"
        },
        "SUCCESS"
    )


    assert result is not None
    assert "feedback" in result
    assert "confidence" in result
    assert result["confidence"] == 10



def test_intelligence_flow_governance_feedback_incorrect():

    flow = IntelligenceFlow()


    record = GovernanceRecord(
        strategy={
            "name": "strategy_alpha"
        },
        status="CONFIRMED",
        reason="valid strategy"
    )


    flow.governance_memory.store(
        record
    )


    flow.update_governance_feedback(
        {
            "name": "strategy_alpha"
        },
        {
            "status": "CONFIRMED"
        }
    )


    result = flow.update_governance_feedback(
        {
            "name": "strategy_alpha"
        },

        "FAILURE"
    )


    assert result["confidence"] == 0