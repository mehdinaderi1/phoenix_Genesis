from intelligence.runtime.runtime_context import (
    RuntimeContext
)

from intelligence.runtime.runtime_priority import (
    RuntimePriorityEngine
)



def test_position_has_highest_priority():

    engine = RuntimePriorityEngine()


    context = RuntimeContext(
        open_position=True,
        signal_ready=True,
        evolution_requested=True
    )


    result = engine.evaluate(
        context
    )


    assert (
        result.priority
        ==
        "POSITION_PROTECTION"
    )



def test_signal_priority_over_learning():

    engine = RuntimePriorityEngine()


    context = RuntimeContext(
        signal_ready=True,
        evolution_requested=True
    )


    result = engine.evaluate(
        context
    )


    assert (
        result.priority
        ==
        "ACTION"
    )



def test_evolution_waits_when_nothing_active():

    engine = RuntimePriorityEngine()


    context = RuntimeContext(
        evolution_requested=True
    )


    result = engine.evaluate(
        context
    )


    assert (
        result.priority
        ==
        "LEARNING"
    )