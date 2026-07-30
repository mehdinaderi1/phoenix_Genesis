from intelligence.governance.governance_intelligence import (
    GovernanceIntelligence
)

from intelligence.governance.governance_memory import (
    GovernanceMemory
)

from intelligence.governance.governance_recall import (
    GovernanceRecall
)



class GovernanceIntelligentGate:


    def __init__(
        self,
        intelligence=None
    ):


        if intelligence:

            self.intelligence = intelligence


        else:

            memory = GovernanceMemory()

            recall = GovernanceRecall(
                memory
            )

            self.intelligence = GovernanceIntelligence(
                recall
            )



    def evaluate(
        self,
        strategy
    ):

    
        recall = getattr(
            self.intelligence,
            "recall",
            None
        )


        if recall:

            matches = recall.find_similar(
                strategy
            )

            if not matches:

                return {
                    "approved": True,
                    "trust": 50,
                    "reason":
                        "No governance history, learning allowed"
                }



        analysis = self.intelligence.analyze(
            strategy
        )


        if (
            analysis["recommendation"]
            ==
            "ALLOW_EVOLUTION"
        ):

            return {

                "approved": True,

                "trust": analysis["trust"],

                "reason":
                    "Governance intelligence approved"

            }


        return {

            "approved": False,

            "trust": analysis["trust"],

            "reason":
                "Governance intelligence restricted evolution"

        }