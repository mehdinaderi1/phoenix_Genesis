from intelligence.governance.governance_feedback_flow import (
    GovernanceFeedbackFlow
)


def test_governance_feedback_flow():


    flow = GovernanceFeedbackFlow()


    result = flow.process(
        "Trend",
        "SUCCESS"
    )


    assert result["success_rate"] == 100

    assert result["trust"]["status"] == "HIGH"