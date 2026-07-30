from intelligence.governance.governance_evolution_controller import (
    GovernanceEvolutionController
)


def test_governance_evolution_controller_default():


    controller = GovernanceEvolutionController()


    result = controller.evaluate()


    assert result["decision"] == (
        "RESTRICT_EVOLUTION"
    )



def test_governance_evolution_controller_allow():


    from intelligence.governance.governance_memory import (
        GovernanceMemory
    )

    from intelligence.governance.governance_record import (
        GovernanceRecord
    )

    from intelligence.governance.governance_learning import (
        GovernanceLearning
    )


    memory = GovernanceMemory()


    memory.store(
        GovernanceRecord(
            strategy="Trend",
            status="APPROVED",
            reason="success"
        )
    )


    controller = GovernanceEvolutionController(
        GovernanceLearning(memory)
    )


    result = controller.evaluate()


    assert result["decision"] == (
        "ALLOW_EVOLUTION"
    )