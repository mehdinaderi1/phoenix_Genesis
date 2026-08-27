from intelligence.meta.meta_insight import MetaInsight


class MetaBiasAnalyzer:


    def detect(
        self,
        meta_insight: MetaInsight
    ):

        if (
            meta_insight.confidence_accuracy < 50
            and
            meta_insight.average_quality < 50
        ):

            return {
                "bias": "OVERCONFIDENT",
                "adjustment": -10
            }


        if (
            meta_insight.confidence_accuracy < 50
            and
            meta_insight.average_quality >= 80
        ):

            return {
                "bias": "UNDERCONFIDENT",
                "adjustment": 5
            }


        return {
            "bias": "NORMAL",
            "adjustment": 0
        }