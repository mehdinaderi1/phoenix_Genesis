class EvolutionConfidence:

    def __init__(
        self
    ):
        self.base_confidence = 50


    def calculate(
        self,
        strategy
    ):

        confidence = self.base_confidence

        reasons = []


        if not isinstance(strategy, dict):

            return {

                "confidence": confidence,

                "reason":
                    "insufficient strategy data"

            }


        score = strategy.get(
            "score",
            0
        )

        success_rate = strategy.get(
            "success_rate",
            0
        )

        generation = strategy.get(
            "generation",
            1
        )


        if score >= 80:

            confidence += 20

            reasons.append(
                "high performance score"
            )


        elif score < 50:

            confidence -= 20

            reasons.append(
                "low performance score"
            )


        if success_rate >= 0.7:

            confidence += 20

            reasons.append(
                "successful evolution history"
            )


        elif success_rate < 0.3:

            confidence -= 20

            reasons.append(
                "poor success rate"
            )


        if generation > 1:

            confidence += 10

            reasons.append(
                "experienced strategy lineage"
            )


        confidence = max(
            0,
            min(
                confidence,
                100
            )
        )


        return {

            "confidence": confidence,

            "reason":
                ", ".join(reasons)

        }