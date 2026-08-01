class LifecycleGovernanceGate:


    def __init__(
        self,
        governance
    ):

        self.governance = governance



    def approve_activation(
        self,
        strategy
    ):

        result = self.governance.evaluate(
            strategy
        )


        if result["status"] == "APPROVED":

            return {

                "allowed": True,

                "reason": result["reason"]

            }


        return {

            "allowed": False,

            "reason": result["reason"]

        }