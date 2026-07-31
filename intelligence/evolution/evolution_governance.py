class EvolutionGovernance:


    def __init__(
        self,
        intelligence,
        governance
    ):

        self.intelligence = intelligence

        self.governance = governance



    def evaluate(
        self,
        strategy
    ):


        evolution_result = (
            self.intelligence.evaluate(
                strategy
            )
        )


        if evolution_result["decision"] != "ALLOW":

            return {

                "status": "BLOCKED",

                "reason": (
                    "Evolution intelligence rejected"
                ),

                "evolution": evolution_result

            }


        governance_result = (
            self.governance.evaluate(
                strategy
            )
        )


        if governance_result["status"] != "APPROVED":

            return {

                "status": "BLOCKED",

                "reason": (
                    "Governance rejected evolution"
                ),

                "governance": governance_result

            }



        return {

            "status": "APPROVED",

            "reason": (
                "Evolution and governance approved"
            ),

            "evolution": evolution_result,

            "governance": governance_result

        }