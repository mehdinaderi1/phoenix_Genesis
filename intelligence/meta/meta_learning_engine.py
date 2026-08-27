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


        if reliability == "HIGH":

            adjustment = 5


        elif reliability == "LOW":

            adjustment = -5


        return {

            "confidence_adjustment": adjustment,

            "reliability": reliability

        }