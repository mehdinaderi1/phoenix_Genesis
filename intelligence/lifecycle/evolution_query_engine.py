"""
Evolution Query Engine

Provides intelligence queries
over strategy evolution memory.
"""


class EvolutionQueryEngine:
    """
    Query layer for evolution intelligence.

    Responsibilities:
    - find best strategy version
    - compare generations
    - retrieve evolution paths
    """


    def __init__(self, memory_graph):
        self.memory = memory_graph


    def get_best_strategy(self, strategies=None):
        """
        Return strategy with highest performance_after.
        """

        events = self.memory.get_all()

        if strategies:
            events = [
                event
                for event in events
                if event["strategy"] in strategies
            ]

        if not events:
            return None


        return max(
            events,
            key=lambda x: (
                x["performance_after"]
                if x["performance_after"] is not None
                else 0
            )
        )


    def get_evolution_path(self, strategy):
        """
        Return strategy evolution path.
        """

        return self.memory.get_lineage(
            strategy
        )


    def get_generation(self, strategy):
        """
        Return strategy generation.
        """

        events = self.memory.find_strategy(
            strategy
        )

        if not events:
            return None

        return events[0]["generation"]