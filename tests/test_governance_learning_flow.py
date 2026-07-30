from intelligence.governance.governance_learning_flow import (
    GovernanceLearningFlow
)


def test_governance_learning_flow_default():


    flow = GovernanceLearningFlow()


    result = flow.analyze()


    assert result["trust"] == 0

    assert (
        result["recommendation"]
        ==
        "RESTRICT_EVOLUTION"
    )