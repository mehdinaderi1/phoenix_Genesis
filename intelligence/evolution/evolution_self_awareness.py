class EvolutionSelfAwareness:


    def __init__(
        self,
        memory_intelligence
    ):

        self.memory_intelligence = (
            memory_intelligence
        )



    def evaluate(
        self,
        strategy
    ):

        analysis = (
            self.memory_intelligence.analyze(
                strategy
            )
        )


        if not analysis["known"]:

            return {

                "generation": 0,

                "maturity":
                    "NEW",

                "health":
                    0,

                "trend":
                    "UNKNOWN"

            }



        generation = (
            analysis["evolution_count"]
            + 1
        )


        best_score = (
            analysis["best_score"]
        )


        if best_score >= 90:

            maturity = "ADVANCED"

        elif best_score >= 70:

            maturity = "DEVELOPING"

        else:

            maturity = "EARLY"



        health = (
            best_score / 100
        )


        if analysis["average_score"] > 60:

            trend = "IMPROVING"

        else:

            trend = "STABLE"



        return {

            "generation":
                generation,

            "maturity":
                maturity,

            "health":
                health,

            "trend":
                trend

        }