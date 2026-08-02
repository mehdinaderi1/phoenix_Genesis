from intelligence.runtime.runtime_task import (
    RuntimeTask
)

from intelligence.runtime.runtime_queue import (
    RuntimeTaskQueue
)



def test_task_queue_storage():

    queue = RuntimeTaskQueue()


    task = RuntimeTask(
        "EVOLUTION_ANALYSIS",
        "LOW"
    )


    queue.add(
        task
    )


    assert queue.count() == 1



def test_high_priority_runs_first():

    queue = RuntimeTaskQueue()


    queue.add(
        RuntimeTask(
            "LEARNING",
            "LOW"
        )
    )


    queue.add(
        RuntimeTask(
            "POSITION_CHECK",
            "HIGH"
        )
    )


    next_task = queue.next_task()


    assert (
        next_task.name
        ==
        "POSITION_CHECK"
    )