from intelligence.governance.governance_history import (
    GovernanceHistory
)


class GovernanceReplay:


    def __init__(
        self,
        history=None
    ):

        self.history = (
            history
            or GovernanceHistory()
        )



    def replay(
        self,
        strategy_name
    ):

        records = (
            self.history.find_by_strategy(
                strategy_name
            )
        )


        if not records:

            return {
                "strategy": strategy_name,
                "history_count": 0,
                "success_rate": 0,
                "recommendation": "UNKNOWN"
            }



        success_count = 0


        for record in records:

            result = record.get(
                "result",
                None
            )


            if result == "SUCCESS":

                success_count += 1



        success_rate = (
            success_count / len(records)
        )



        if success_rate >= 0.7:

            recommendation = "TRUST"


        elif success_rate >= 0.4:

            recommendation = "WATCH"


        else:

            recommendation = "AVOID"



        return {
            "strategy": strategy_name,
            "history_count": len(records),
            "success_rate": success_rate,
            "recommendation": recommendation
        }