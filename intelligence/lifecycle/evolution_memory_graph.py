"""
Evolution Memory Graph

Stores strategy evolution history
with lineage and performance context.
"""


class EvolutionMemoryGraph:
    """
    Memory layer for strategy evolution.

    Responsibilities:
    - store evolution events
    - track lineage
    - recall evolution history
    - compare generations
    """

    def __init__(self):
        self.memory = []


    def add_event(
        self,
        strategy,
        parent_strategy=None,
        generation=0,
        action=None,
        reason=None,
        performance_before=None,
        performance_after=None
    ):
        """
        Store evolution event.
        """

        event = {
            "strategy": strategy,
            "parent_strategy": parent_strategy,
            "generation": generation,
            "action": action,
            "reason": reason,
            "performance_before": performance_before,
            "performance_after": performance_after
        }

        self.memory.append(event)

        return event


    def get_all(self):
        """
        Return all evolution memories.
        """

        return self.memory


    def find_strategy(self, strategy):
        """
        Find evolution memory by strategy.
        """

        return [
            event
            for event in self.memory
            if event["strategy"] == strategy
        ]


    def get_lineage(self, strategy):
        """
        Reconstruct strategy ancestry.
        """

        lineage = []

        current = strategy

        while current:

            lineage.append(current)

            parent = None

            for event in self.memory:

                if event["strategy"] == current:
                    parent = event["parent_strategy"]
                    break

            current = parent

        return lineage