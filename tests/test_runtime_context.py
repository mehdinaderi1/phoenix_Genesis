from intelligence.runtime.runtime_context import (
    RuntimeContext
)



def test_runtime_context_creation():

    context = RuntimeContext(
        signal_ready=True,
        memory_queries=3,
        evolution_requested=True
    )


    assert context.signal_ready is True

    assert context.memory_queries == 3

    assert context.evolution_requested is True



def test_runtime_context_export():

    context = RuntimeContext(
        strategy="momentum_v2"
    )


    data = context.to_dict()


    assert data["strategy"] == "momentum_v2"