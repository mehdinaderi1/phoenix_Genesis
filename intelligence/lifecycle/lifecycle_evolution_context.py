"""
Lifecycle Evolution Context

Builds intelligence context from previous
strategy evolution experiences.
"""


class LifecycleEvolutionContext:
    """
    Provides evolution knowledge context
    for lifecycle decisions.
    """

    def __init__(self, evolution_recall):
        self.evolution_recall = evolution_recall


    def build(self, strategy):
        """
        Create evolution context for strategy.
        """

        history = self.evolution_recall.recall(
            strategy
        )

        return {
            "strategy": strategy,
            "has_history": bool(history),
            "evolution_count": len(history),
            "last_evolution": (
                history[-1]
                if history
                else None
            ),
            "history": history
        }


    def has_previous_evolution(self, strategy):
        """
        Check existing evolution knowledge.
        """

        return self.evolution_recall.has_evolved(
            strategy
        )