class MetaLearningEngine:


    def learn(
        self,
        meta_insight
    ):

        if meta_insight is None:

            return {
                "confidence_adjustment": 0,
                "learning": "NO_DATA"
            }


        adjustment = 0


        reliability = getattr(
            meta_insight,
            "reliability",
            "UNKNOWN"
        )


        if (
            reliability == "HIGH"
            and meta_insight.samples >= 10
        ):

            adjustment = 5


        elif (
            reliability == "LOW"
            and meta_insight.samples >= 10
        ):

            adjustment = -5


        if meta_insight.samples >= 10:

            bias = getattr(
                meta_insight,
                "bias",
                None
            )

            if isinstance(bias, dict):

                adjustment += bias.get(
                    "adjustment",
                    0
                )


        learning_reliability = "UNKNOWN"


        meta_feedback = getattr(
            meta_insight,
            "meta_feedback",
            None
        )


        if isinstance(meta_feedback, dict):

            success_rate = meta_feedback.get(
                "success_rate"
            )


            if success_rate is not None:

                if success_rate >= 0.6:

                    learning_reliability = "HIGH"

                elif success_rate >= 0.4:

                    learning_reliability = "MEDIUM"

                else:

                    learning_reliability = "LOW"


        return {

            "confidence_adjustment": adjustment,

            "reliability": reliability,

            "learning_reliability": learning_reliability

        }
