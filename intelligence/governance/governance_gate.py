class GovernanceGate:


    def __init__(
        self,
        minimum_confidence=0
    ):

        self.minimum_confidence = (
            minimum_confidence
        )



    def evaluate(
        self,
        governance_state
    ):

        status = governance_state.get(
            "status",
            "UNKNOWN"
        )

        confidence = governance_state.get(
            "confidence",
            0
        )


        if status == "REJECTED":

            return {
                "approved": False,
                "reason": "governance rejected"
            }


        if confidence < self.minimum_confidence:

            return {
                "approved": False,
                "reason": "low governance confidence"
            }


        return {
            "approved": True,
            "reason": "governance approved"
        }