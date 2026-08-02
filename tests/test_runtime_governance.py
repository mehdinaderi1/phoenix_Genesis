from intelligence.runtime.intelligence_budget import (
    IntelligenceBudget
)

from intelligence.runtime.runtime_policy import (
    RuntimePolicy
)

from intelligence.runtime.runtime_guardian import (
    RuntimeGuardian
)



def test_runtime_blocks_memory_overuse():

    budget = IntelligenceBudget(
        max_memory_lookup=5
    )

    policy = RuntimePolicy()

    guardian = RuntimeGuardian(
        budget,
        policy
    )


    result = guardian.check(
        {
            "signal_ready": True,
            "memory_queries": 10
        }
    )


    assert result.allowed is False

    assert (
        result.reason
        ==
        "memory_budget_exceeded"
    )



def test_runtime_allows_normal_decision():

    budget = IntelligenceBudget()

    policy = RuntimePolicy()

    guardian = RuntimeGuardian(
        budget,
        policy
    )


    result = guardian.check(
        {
            "signal_ready": True,
            "memory_queries": 2
        }
    )


    assert result.allowed is True