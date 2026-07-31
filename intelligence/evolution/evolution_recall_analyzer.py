class EvolutionRecallAnalyzer:


    def __init__(
        self,
        recall
    ):

        self.recall = recall



    def analyze(
        self,
        strategy_name
    ):

        lineage = self.recall.find_lineage(
            strategy_name
        )


        if not lineage:

            return {

                "history_found": False,

                "success_rate": 0,

                "recommendation": "NEW"

            }



        success = 0


        for record in lineage:

            if record.score_after > record.score_before:

                success += 1



        success_rate = (
            success / len(lineage)
        )


        if success_rate >= 0.7:

            recommendation = "EVOLVE"


        else:

            recommendation = "CAUTION"



        return {

            "history_found": True,

            "generations": len(lineage),

            "success_rate": success_rate,

            "recommendation": recommendation

        }