class RuntimePriorityDecision:

    def __init__(
        self,
        priority,
        reason
    ):

        self.priority = priority
        self.reason = reason



class RuntimePriorityEngine:


    def evaluate(
        self,
        context
    ):

        # Highest priority:
        # protect existing positions

        if context.open_position:

            return RuntimePriorityDecision(
                "POSITION_PROTECTION",
                "open_position_requires_attention"
            )


        # Trading action has priority
        # over learning/evolution

        if context.signal_ready:

            return RuntimePriorityDecision(
                "ACTION",
                "active_signal_detected"
            )


        # Learning before evolution

        if (
            context.evolution_requested
        ):

            return RuntimePriorityDecision(
                "LEARNING",
                "evolution_request_pending"
            )


        return RuntimePriorityDecision(
            "WAIT",
            "nothing_requires_execution"
        )