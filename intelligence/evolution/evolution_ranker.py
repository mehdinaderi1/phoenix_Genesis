class EvolutionRanker:


    def rank(
        self,
        lineage
    ):

        if not lineage:

            return {
                "score": 0,
                "rank": "UNKNOWN",
                "evolutions": 0
            }


        total_improvement = 0
        generations = len(lineage)


        for record in lineage:

            improvement = (
                record.score_after
                -
                record.score_before
            )

            total_improvement += improvement


        average_improvement = (
            total_improvement / generations
        )


        if average_improvement >= 10:

            rank = "EXCELLENT"


        elif average_improvement >= 5:

            rank = "GOOD"


        elif average_improvement > 0:

            rank = "STABLE"


        else:

            rank = "WEAK"


        return {

            "score": average_improvement,

            "rank": rank,

            "evolutions": generations

        }