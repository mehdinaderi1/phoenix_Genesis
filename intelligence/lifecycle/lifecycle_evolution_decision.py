"""
Lifecycle Evolution Decision Intelligence

Makes lifecycle decisions using strategy state
and previous evolution context.
"""


class LifecycleEvolutionDecision:
    """
    Intelligent lifecycle decision layer.

    Decisions:
    - KEEP
    - IMPROVE
    - ARCHIVE
    - EVALUATE
    """

    def decide(
        self,
        strategy_score,
        evolution_context
    ):
        """
        Decide lifecycle action.
        """

        has_history = evolution_context.get(
            "has_history",
            False
        )

        evolution_count = evolution_context.get(
            "evolution_count",
            0
        )


        # Healthy strategy
        if strategy_score >= 80:
            return "KEEP"


        # Poor strategy without evolution history
        if (
            strategy_score < 50
            and not has_history
        ):
            return "IMPROVE"


        # Repeated evolution without success
        if (
            strategy_score < 50
            and evolution_count >= 2
        ):
            return "ARCHIVE"


        # Default evaluation path
        return "EVALUATE"