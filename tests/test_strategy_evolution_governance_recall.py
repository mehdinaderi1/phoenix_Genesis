from intelligence.learning.strategy_evolution_flow import (
    StrategyEvolutionFlow
)

from intelligence.governance.governance_memory import (
    GovernanceMemory
)

from intelligence.governance.governance_record import (
    GovernanceRecord
)

from intelligence.governance.governance_recall_flow import (
    GovernanceRecallFlow
)



def test_strategy_evolution_contains_governance_recall():


    memory = GovernanceMemory()


    memory.store(
        GovernanceRecord(
            strategy={
                "risk": "LOW"
            },
            status="APPROVED",
            reason="previous success"
        )
    )


    recall_flow = GovernanceRecallFlow(
        memory=memory
    )


    flow = StrategyEvolutionFlow(
        governance_recall_flow=recall_flow
    )


    result = flow.evaluate(
        {
            "risk": "LOW"
        },
        [
            {
                "score": 90,
                "success": True
            }
        ]
    )


    assert "governance_recall" in result

    assert (
        result["governance_recall"]["matches"]
        == 1
    )