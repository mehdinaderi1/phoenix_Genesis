from intelligence.governance.governance_memory import (
    GovernanceMemory
)

from intelligence.governance.governance_record import (
    GovernanceRecord
)

from intelligence.governance.governance_recall import (
    GovernanceRecall
)

from intelligence.governance.governance_intelligence import (
    GovernanceIntelligence
)



def test_governance_intelligence_trust():


    memory = GovernanceMemory()


    memory.store(
        GovernanceRecord(
            strategy={
                "risk": "LOW"
            },
            status="APPROVED",
            reason="success"
        )
    )


    recall = GovernanceRecall(
        memory
    )


    intelligence = GovernanceIntelligence(
        recall
    )


    result = intelligence.analyze(
        {
            "risk": "LOW"
        }
    )


    assert result["trust"] == 100

    assert (
        result["recommendation"]
        ==
        "ALLOW_EVOLUTION"
    )