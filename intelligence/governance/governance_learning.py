from intelligence.governance.governance_memory import (
    GovernanceMemory
)


class GovernanceLearning:


    def __init__(
        self,
        memory=None
    ):

        self.memory = (
            memory
            or GovernanceMemory()
        )



    def analyze_history(
        self
    ):

        total = self.memory.count()


        if total == 0:

            return {
                "samples": 0,
                "success_rate": 0,
                "trust": 0
            }



        confirmed = len(
            self.memory.find_by_status(
                "APPROVED"
            )
        )


        success_rate = (
            confirmed / total
        )



        trust = int(
            success_rate * 100
        )



        return {
            "samples": total,
            "success_rate": success_rate,
            "trust": trust
        }



    def calculate_trust(
        self
    ):

        analysis = self.analyze_history()

        return analysis["trust"]



    def recommend(
        self
    ):

        trust = self.calculate_trust()



        if trust >= 70:

            return {
                "recommendation": "ALLOW_EVOLUTION",
                "trust": trust,
                "reason": (
                    "Governance history is reliable"
                )
            }



        return {
            "recommendation": "RESTRICT_EVOLUTION",
            "trust": trust,
            "reason": (
                "Governance confidence is low"
            )
        }