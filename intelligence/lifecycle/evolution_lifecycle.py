"""
Evolution Lifecycle Controller

Coordinates complete strategy evolution flow.
"""


class EvolutionLifecycle:

    def __init__(
        self,
        ranker,
        selector,
        governance,
        history
    ):
        self.ranker = ranker
        self.selector = selector
        self.governance = governance
        self.history = history


    def evolve(self, candidates):
        """
        Execute full evolution lifecycle.

        Flow:
        Rank
        Select
        Govern
        Store
        """

        if not candidates:
            return None


        selected = self.selector.select(
            candidates
        )


        if not selected:
            return None


        lineage = selected["lineage"]

        record = lineage[-1]


        approval = self.governance.evaluate(
            record
        )


        if approval["status"] != "APPROVED":
            return {
                "status": "REJECTED",
                "reason": approval["reason"]
            }


        self.history.add(
            record
        )


        return {
            "status": "APPROVED",
            "strategy": record.child,
            "score": record.score_after
        }