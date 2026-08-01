"""
Strategy Lineage Tracker

Tracks strategy evolution tree and ancestry.
"""


class StrategyLineageTracker:
    """
    Maintains strategy evolution lineage.

    Responsibilities:
    - register strategy versions
    - track parents
    - retrieve ancestry
    - retrieve descendants
    """

    def __init__(self):
        self.nodes = {}


    def register(
        self,
        strategy,
        parent_strategy=None,
        generation=0
    ):
        """
        Register strategy lineage node.
        """

        self.nodes[strategy] = {
            "strategy": strategy,
            "parent_strategy": parent_strategy,
            "generation": generation,
            "children": []
        }

        if parent_strategy in self.nodes:
            self.nodes[parent_strategy]["children"].append(strategy)

        return self.nodes[strategy]


    def get(self, strategy):
        """
        Retrieve lineage node.
        """

        return self.nodes.get(strategy)


    def get_parent(self, strategy):
        """
        Return parent strategy.
        """

        node = self.nodes.get(strategy)

        if not node:
            return None

        return node["parent_strategy"]


    def get_children(self, strategy):
        """
        Return child strategies.
        """

        node = self.nodes.get(strategy)

        if not node:
            return []

        return node["children"]


    def get_ancestry(self, strategy):
        """
        Return full lineage chain.
        """

        lineage = []

        current = strategy

        while current:

            lineage.append(current)

            current = self.get_parent(current)

        return lineage