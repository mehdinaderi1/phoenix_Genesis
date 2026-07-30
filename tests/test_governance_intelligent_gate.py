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

from intelligence.governance.governance_intelligent_gate import (
    GovernanceIntelligentGate
)



def test_intelligent_gate_allows_success_history():


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


    gate = GovernanceIntelligentGate(
        intelligence
    )


    result = gate.evaluate(
        {
            "risk": "LOW"
        }
    )


    assert result["approved"] is True



def test_intelligent_gate_blocks_bad_history():


    memory = GovernanceMemory()


    memory.store(
        GovernanceRecord(
            strategy={
                "risk": "HIGH"
            },
            status="REJECTED",
            reason="failed"
        )
    )


    recall = GovernanceRecall(
        memory
    )


    intelligence = GovernanceIntelligence(
        recall
    )


    gate = GovernanceIntelligentGate(
        intelligence
    )


    result = gate.evaluate(
        {
            "risk": "HIGH"
        }
    )


    assert result["approved"] is False