from intelligence.flow import IntelligenceFlow

from intelligence.evolution.self_evolution_controller import (
    SelfEvolutionController,
)


def test_intelligence_flow_has_self_evolution_controller():

    flow = IntelligenceFlow()

    assert hasattr(
        flow,
        "self_evolution_controller"
    )

    assert isinstance(
        flow.self_evolution_controller,
        SelfEvolutionController
    )