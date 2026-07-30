from intelligence.governance.governance_learning import (
    GovernanceLearning
)

from intelligence.governance.governance_memory import (
    GovernanceMemory
)

from intelligence.governance.governance_record import (
    GovernanceRecord
)



def test_governance_learning_trust():

    memory = GovernanceMemory()


    memory.store(
        GovernanceRecord(
            strategy={
                "name": "Trend"
            },
            status="APPROVED",
            reason="success"
        )
    )


    learning = GovernanceLearning(
        memory
    )


    result = learning.analyze_history()


    assert result["trust"] == 100



def test_governance_learning_recommend():

    learning = GovernanceLearning()


    result = learning.recommend()


    assert result["recommendation"] == (
        "RESTRICT_EVOLUTION"
    )