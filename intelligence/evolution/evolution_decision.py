class EvolutionDecision:

    def decide(
        self,
        current_score,
        parent_score
    ):

        if current_score >= parent_score:

            return {
                "decision": "KEEP",
                "reason": "performance improved"
            }


        if current_score < parent_score:

            return {
                "decision": "ROLLBACK",
                "reason": "performance degraded"
            }


        return {
            "decision": "EVOLVE",
            "reason": "needs improvement"
        }