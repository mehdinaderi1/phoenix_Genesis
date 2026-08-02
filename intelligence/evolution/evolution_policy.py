class EvolutionPolicy:


    def __init__(
        self,
        max_generation=5,
        min_confidence=70,
        allow_retirement=True
    ):

        self.max_generation = max_generation

        self.min_confidence = min_confidence

        self.allow_retirement = allow_retirement



    def evaluate(
        self,
        evolution
    ):

        generation = evolution.get(
            "generation",
            0
        )


        confidence = evolution.get(
            "confidence",
            0
        )


        decision = evolution.get(
            "decision",
            "UNKNOWN"
        )


        if generation > self.max_generation:

            return {

                "allowed": False,

                "reason":
                    "generation limit reached"

            }



        if confidence < self.min_confidence:

            return {

                "allowed": False,

                "reason":
                    "confidence below policy threshold"

            }



        if (
            decision == "RETIRE"
            and not self.allow_retirement
        ):

            return {

                "allowed": False,

                "reason":
                    "retirement disabled"

            }



        return {

            "allowed": True,

            "reason":
                "policy satisfied"

        }