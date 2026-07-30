class GovernanceEvolution:


    def evaluate(
        self,
        governance_result
    ):


        status = governance_result.get(
            "status"
        )


        confidence = governance_result.get(
            "confidence",
            0
        )


        if (
            status == "STABLE"
            and confidence >= 10
        ):

            return {
                "decision": "ALLOW_EVOLUTION",
                "reason": "governance confidence is stable"
            }



        elif confidence < 10:

            return {
                "decision": "REVIEW",
                "reason": "insufficient governance confidence"
            }



        else:

            return {
                "decision": "BLOCK_EVOLUTION",
                "reason": "governance status not approved"
            }