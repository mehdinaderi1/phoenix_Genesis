from intelligence.governance.governance_learning import (
    GovernanceLearning
)


class GovernanceLearningFlow:


    def __init__(
        self,
        learning=None
    ):

        self.learning = (
            learning
            or GovernanceLearning()
        )


    def analyze(
        self
    ):

        result = (
            self.learning.analyze_history()
        )


        recommendation = (
            self.learning.recommend()
        )


        return {
            "trust": result.get(
                "trust",
                0
            ),

            "approved": result.get(
                "approved",
                0
            ),

            "rejected": result.get(
                "rejected",
                0
            ),

            "recommendation": recommendation.get(
                "recommendation",
                "RESTRICT_EVOLUTION"
            )
        }