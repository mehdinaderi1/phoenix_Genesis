from intelligence.runtime.runtime_context import RuntimeContext

class RuntimeDecision:

    def __init__(
        self,
        allowed,
        reason
    ):

        self.allowed = allowed
        self.reason = reason



class RuntimeGuardian:


    def __init__(
        self,
        budget,
        policy
    ):

        self.budget = budget
        self.policy = policy



    def check(
        self,
        context
    ):


        if isinstance(context, dict):
            context = RuntimeContext(**context)

        if (
            not context.signal_ready
        ):

            return RuntimeDecision(
                False,
                "no_action_priority"
            )


        if not self.budget.allow_memory_lookup(
            context.memory_queries
        ):

            return RuntimeDecision(
                False,
                "memory_budget_exceeded"
            )


        return RuntimeDecision(
            True,
            "runtime_allowed"
        )