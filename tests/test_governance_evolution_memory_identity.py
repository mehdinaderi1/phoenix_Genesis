from intelligence.components.intelligence_components import IntelligenceComponents
from intelligence.learning.strategy_evolution_flow import StrategyEvolutionFlow


def test_strategy_evolution_flow_uses_shared_governance_memory():
    components = IntelligenceComponents()

    flow = StrategyEvolutionFlow(
        performance_analyzer=components.strategy_performance,
        evolution_decision=components.strategy_evolution_decision,
        governance_memory=components.governance_memory,
    )

    assert flow.governance_memory is components.governance_memory


def test_evolution_memory_uses_same_governance_memory():
    components = IntelligenceComponents()

    flow = StrategyEvolutionFlow(
        performance_analyzer=components.strategy_performance,
        evolution_decision=components.strategy_evolution_decision,
        governance_memory=components.governance_memory,
    )

    assert flow.evolution_memory.memory is flow.governance_memory

def test_evolution_memory_stores_into_shared_governance_memory():
    components = IntelligenceComponents()

    flow = StrategyEvolutionFlow(
        performance_analyzer=components.strategy_performance,
        evolution_decision=components.strategy_evolution_decision,
        governance_memory=components.governance_memory,
    )

    before = flow.governance_memory.count()

    flow.evolution_memory.store(
        {"name": "S"},
        "IMPROVE",
        75
    )

    assert flow.governance_memory.count() == before + 1
    assert flow.governance_memory.latest()["decision"] == "IMPROVE"