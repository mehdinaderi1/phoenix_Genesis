class EvolutionExplainer:


    def explain(
        self,
        record
    ):

        improvement = (
            record.score_after
            -
            record.score_before
        )


        if improvement > 0:

            status = "improved"

        elif improvement < 0:

            status = "degraded"

        else:

            status = "unchanged"



        return {

            "strategy_change":
                f"{record.parent} -> {record.child}",


            "improvement":
                improvement,


            "status":
                status,


            "reason":
                record.reason,


            "generation":
                record.generation,


            "explanation":
                (
                    f"Strategy evolved from "
                    f"{record.parent} to {record.child}. "
                    f"Performance {status} by "
                    f"{abs(improvement)} points "
                    f"because of {record.reason}."
                )

        }