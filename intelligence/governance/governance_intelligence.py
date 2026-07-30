from intelligence.governance.governance_recall import (
    GovernanceRecall
)


class GovernanceIntelligence:


    def __init__(
        self,
        recall
    ):

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


        total = len(records)


        if total == 0:

            return {

                "matches": 0,

                "approved": 0,

                "rejected": 0,

                "trust": 0,

                "recommendation":
                    "NO_HISTORY"

            }



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


        trust = int(
            approved * 100 / total
        )


        if trust >= 70:

            recommendation = (
                "ALLOW_EVOLUTION"
            )

        else:

            recommendation = (
                "RESTRICT_EVOLUTION"
            )



        return {

            "matches": total,

            "approved": approved,

            "rejected": rejected,

            "trust": trust,

            "recommendation":
                recommendation

        }