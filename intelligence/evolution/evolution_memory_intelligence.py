class EvolutionMemoryIntelligence:


    def __init__(
        self,
        memory
    ):

        self.memory = memory



    def analyze(
        self,
        strategy
    ):

        records = self.memory.recall(
            strategy
        )


        if not records:

            return {

                "known":
                    False,

                "evolution_count":
                    0,

                "average_score":
                    0,

                "best_score":
                    0

            }



        scores = [

            record.score_after

            for record in records

        ]


        return {

            "known":
                True,

            "evolution_count":
                len(records),

            "average_score":
                sum(scores) / len(scores),

            "best_score":
                max(scores)

        }



    def should_evolve(
        self,
        strategy
    ):

        analysis = self.analyze(
            strategy
        )


        if not analysis["known"]:

            return True



        if analysis["best_score"] >= 90:

            return False



        return True