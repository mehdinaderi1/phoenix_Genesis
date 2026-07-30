from intelligence.governance.governance_memory import (
    GovernanceMemory
)


class GovernanceFeedback:


    def __init__(
        self,
        memory=None
    ):

        self.memory = (
            memory
            or GovernanceMemory()
        )



    def record(
        self,
        strategy,
        result
    ):


        feedback = {

            "strategy": strategy,

            "result": result

        }


        self.memory.store(
            {
                "strategy": strategy,
                "result": result,
                "status": (
                    "APPROVED"
                    if result == "SUCCESS"
                    else "REJECTED"
                )
            }
        )


        return feedback



    def evaluate(
        self,
        strategy,
        outcome
    ):


        self.record(
            strategy,
            outcome
        )


        approved = (
            outcome == "SUCCESS"
        )


        return {

            "strategy": strategy,

            "outcome": outcome,

            "approved": approved,

            "status": (
                "CONFIRMED"
                if approved
                else "INCORRECT"
            )

        }



    def success_rate(
        self
    ):


        records = self.memory.get_all()


        if not records:

            return 0



        success = sum(

            1
            for item in records
            if item.get("result") == "SUCCESS"

        )


        return int(
            success * 100 / len(records)
        )