from intelligence.flow import IntelligenceFlow


def test_self_evolution_creates_lineage():

    flow = IntelligenceFlow()

    strategy = {
        "name": "MomentumStrategy",
        "generation": 1,
        "score": 80,
        "success_rate": 0.8
    }


    result = (
        flow.self_evolution_controller.run(
            strategy,
            80
        )
    )

    print("RESULT:", result)
    print("HISTORY:", flow.evolution_history.all())
    assert result is not None


    history = (
        flow.evolution_history
    )


    record = history.latest()


    assert record is not None


    assert record.parent == (
        "MomentumStrategy"
    )


    assert record.child == (
        "MomentumStrategy_v2"
    )


    print("RESULT:", result)
    print("HISTORY:", flow.evolution_history.all())
    assert record.generation == 2