"""
Evolution Selector

Selects the best evolution candidate.
"""


class EvolutionSelector:

    def __init__(self, engine):
        self.engine = engine


    def select(self, lineages):
        """
        Select best lineage using ranker.
        """

        if not lineages:
            return None


        results = []

        for lineage in lineages:

            analysis = self.engine.rank(
                lineage
            )

            results.append(
                {
                    "lineage": lineage,
                    "analysis": analysis
                }
            )


        return max(
            results,
            key=lambda item:
            item["analysis"]["score"]
        )


    def select_best_branch(self, strategy_family):
        """
        Compatibility with memory graph.
        """

        events = [
            event
            for event in self.engine.get_all()
            if (
                event["strategy"] == strategy_family
                or
                event.get("parent_strategy") == strategy_family
            )
        ]


        if not events:
            return None


        return max(
            events,
            key=lambda x:
            x.get(
                "performance_after",
                0
            )
        )