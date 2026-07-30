from intelligence.governance.governance_recall_flow import (
    GovernanceRecallFlow
)


def test_governance_recall_flow_empty():

    flow = GovernanceRecallFlow()


    result = flow.analyze(
        {
            "risk": "LOW"
        }
    )


    assert result["matches"] == 0