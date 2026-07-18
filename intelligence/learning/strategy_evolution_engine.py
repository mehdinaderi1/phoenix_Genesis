class StrategyEvolutionEngine:


    def evaluate(
        self,
        strategy
    ):

        score = strategy.get(
            "score",
            0
        )

        success_rate = strategy.get(
            "success_rate",
            0
        )


        if (
            score >= 80
            and success_rate >= 0.7
        ):

            decision = "KEEP"


        elif (
            score < 50
            or success_rate < 0.3
        ):

            decision = "RETIRE"


        else:

            decision = "IMPROVE"


        return {

            "decision": decision,

            "score": score,

            "success_rate": success_rate

        }



    def evolve(
        self,
        strategy,
        score
    ):

        if score < 70:

            return {
                "strategy": strategy,
                "parent": None,
                "score": score,
                "generation": 1,
                "evolved": False
            }


        return {

            "strategy": strategy + "_v2",

            "parent": strategy,

            "score": score + 10,

            "generation": 2,

            "evolved": True

        }