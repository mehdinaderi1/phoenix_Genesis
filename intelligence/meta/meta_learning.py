from intelligence.meta.meta_insight import MetaInsight


class MetaLearning:


    def analyze(
        self,
        meta_insight: MetaInsight
    ):

        recommendation = (
            "MAINTAIN_CONFIDENCE"
        )

        adjustment = 0


        if meta_insight.bias == "OVERCONFIDENT":

            recommendation = (
                "REDUCE_CONFIDENCE"
            )

            adjustment = -10


        elif meta_insight.bias == "UNDERCONFIDENT":

            recommendation = (
                "INCREASE_CONFIDENCE"
            )

            adjustment = 5


        return {

            "recommendation": recommendation,

            "confidence_adjustment": adjustment,

            "reliability": (
                meta_insight.reliability
            )

        }