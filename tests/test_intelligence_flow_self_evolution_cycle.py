from intelligence.flow import IntelligenceFlow


def test_flow_self_evolution_history_connection():

    flow = IntelligenceFlow()

    controller = flow.self_evolution_controller

    assert controller is not None

    assert flow.evolution_history is (
        controller.history
    )