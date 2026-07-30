from intelligence.governance.governance_memory import (
    GovernanceMemory
)

from intelligence.governance.governance_record import (
    GovernanceRecord
)

from intelligence.governance.governance_recall import (
    GovernanceRecall
)



def test_governance_recall():

    memory = GovernanceMemory()


    memory.store(
        GovernanceRecord(
            strategy={
                "risk": "HIGH"
            },
            status="REJECTED",
            reason="high risk"
        )
    )


    recall = GovernanceRecall(
        memory
    )


    result = recall.find_similar(
        {
            "risk": "HIGH"
        }
    )


    assert len(result) == 1