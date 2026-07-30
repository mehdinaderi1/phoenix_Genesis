from intelligence.governance.governance_evolution_memory import (
    GovernanceEvolutionMemory
)


def test_governance_evolution_memory_store():

    memory = GovernanceEvolutionMemory()


    result = memory.store(
        "Trend",
        "EVOLVE",
        90
    )


    assert result["decision"] == "EVOLVE"
    assert memory.count() == 1