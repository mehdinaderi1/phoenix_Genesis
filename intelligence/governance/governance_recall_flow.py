from intelligence.governance.governance_recall import (
    GovernanceRecall
)

from intelligence.governance.governance_memory import (
    GovernanceMemory
)


class GovernanceRecallFlow:


    def __init__(
        self,
        recall=None,
        memory=None
    ):

        if memory is None:
            memory = GovernanceMemory()

        self.memory = memory


        if recall is None:
            recall = GovernanceRecall(
                self.memory
            )

        self.recall = recall



    def analyze(
        self,
        strategy
    ):

        records = (
            self.recall.find_similar(
                strategy
            )
        )


        approved = sum(
            1
            for record in records
            if record.status == "APPROVED"
        )


        rejected = sum(
            1
            for record in records
            if record.status == "REJECTED"
        )


        return {
            "strategy": strategy,
            "matches": len(records),
            "approved": approved,
            "rejected": rejected
        }