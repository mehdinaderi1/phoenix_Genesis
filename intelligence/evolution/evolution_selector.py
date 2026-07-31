class EvolutionSelector:


    def __init__(
        self,
        ranker
    ):

        self.ranker = ranker



    def select(
        self,
        lineages
    ):


        if not lineages:

            return None



        best = None

        best_score = float(
            "-inf"
        )


        for lineage in lineages:


            result = self.ranker.rank(
                lineage
            )


            score = result["score"]


            if score > best_score:

                best_score = score

                best = {

                    "lineage": lineage,

                    "analysis": result

                }



        return best