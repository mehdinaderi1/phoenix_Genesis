class EvolutionGovernor:


    def decide(
        self,
        awareness
    ):


        maturity = awareness.get(
            "maturity",
            "NEW"
        )

        health = awareness.get(
            "health",
            0
        )

        trend = awareness.get(
            "trend",
            "UNKNOWN"
        )


        if (
            maturity == "ADVANCED"
            and health >= 0.9
            and trend == "IMPROVING"
        ):

            return {

                "decision":
                    "APPROVE",

                "reason":
                    "healthy evolution state"

            }



        if health < 0.4:

            return {

                "decision":
                    "RETIRE",

                "reason":
                    "poor evolution health"

            }



        return {

            "decision":
                "HOLD",

            "reason":
                "needs more evaluation"

        }