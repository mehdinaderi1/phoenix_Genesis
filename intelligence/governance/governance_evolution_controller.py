from intelligence.governance.governance_learning import (
    GovernanceLearning
)


class GovernanceEvolutionController:


    def __init__(
        self,
        learning=None
    ):

        self.learning = (
            learning
            or GovernanceLearning()
        )



    def evaluate(
        self
    ):


        analysis = (
            self.learning.analyze_history()
        )


        trust = analysis["trust"]


        if trust >= 70:

            return {

                "decision": "ALLOW_EVOLUTION",

                "trust": trust,

                "reason":
                    "Governance trust is sufficient"

            }



        return {

            "decision": "RESTRICT_EVOLUTION",

            "trust": trust,

            "reason":
                "Governance trust is insufficient"

        }