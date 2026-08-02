from intelligence.runtime.runtime_context import RuntimeContext
from intelligence.runtime.runtime_priority import RuntimePriorityEngine
from intelligence.runtime.runtime_queue import RuntimeTaskQueue
from intelligence.runtime.runtime_scheduler import RuntimeScheduler
from intelligence.runtime.runtime_task import RuntimeTask


def test_runtime_governance_full_cycle():

    context = RuntimeContext(
        signal_ready=True,
        open_position=True,
        critical_market=True,
        memory_queries=500,
        analysis_depth=5,
        evolution_requested=True,
        strategy="momentum"
    )


    # Priority evaluation

    priority_engine = RuntimePriorityEngine()

    decision = priority_engine.evaluate(
        context
    )


    assert decision.priority == "POSITION_PROTECTION"

    assert (
        decision.reason
        ==
        "open_position_requires_attention"
    )


    # Background scheduling protection

    scheduler = RuntimeScheduler()

    schedule = scheduler.can_process_background(
        context
    )


    assert schedule.allowed is False

    assert (
        schedule.reason
        ==
        "critical_market"
    )


    # Evolution task enters queue

    queue = RuntimeTaskQueue()


    evolution_task = RuntimeTask(
        name="strategy_evolution",
        priority="LOW"
    )


    queue.add(
        evolution_task
    )


    assert queue.count() == 1


    next_task = queue.next_task()


    assert next_task.name == "strategy_evolution"

    assert next_task.status == "PENDING"