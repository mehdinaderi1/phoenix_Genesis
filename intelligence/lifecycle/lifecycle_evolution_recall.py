"""
Lifecycle Evolution Recall

Provides historical evolution knowledge
for future lifecycle decisions.
"""


class LifecycleEvolutionRecall:
    """
    Retrieves previous lifecycle evolution experiences.

    Responsibilities:
    - recall strategy evolution history
    - find previous actions
    - provide evolution context
    """

    def __init__(self, evolution_repository):
        self.evolution_repository = evolution_repository


    def recall(self, strategy):
        """
        Retrieve evolution history for strategy.
        """

        return self.evolution_repository.find_by_strategy(
            strategy
        )


    def latest(self, strategy):
        """
        Return latest evolution event for strategy.
        """

        history = self.recall(strategy)

        if not history:
            return None

        return history[-1]


    def has_evolved(self, strategy):
        """
        Check whether strategy has previous evolution.
        """

        return bool(
            self.recall(strategy)
        )