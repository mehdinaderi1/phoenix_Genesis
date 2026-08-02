from intelligence.runtime.runtime_context import (
    RuntimeContext
)

from intelligence.runtime.runtime_scheduler import (
    RuntimeScheduler
)



def test_scheduler_blocks_during_critical_market():

    scheduler = RuntimeScheduler()


    context = RuntimeContext(
        critical_market=True
    )


    result = scheduler.can_process_background(
        context
    )


    assert result.allowed is False

    assert (
        result.reason
        ==
        "critical_market"
    )



def test_scheduler_allows_when_safe():

    scheduler = RuntimeScheduler()


    context = RuntimeContext()


    result = scheduler.can_process_background(
        context
    )


    assert result.allowed is True