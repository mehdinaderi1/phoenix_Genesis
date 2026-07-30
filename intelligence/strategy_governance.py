class StrategyGovernance:

    def evaluate(
        self,
        strategy
    ):

        score = strategy.get(
            "score",
            0
        )

        confidence = strategy.get(
            "confidence",
            0
        )

        risk = strategy.get(
            "risk",
            "HIGH"
        )


        # Risk has highest priority
        if risk == "HIGH":

            return {
                "status": "REJECTED",
                "reason": "High risk strategy"
            }


        if (
            score >= 80
            and confidence >= 70
        ):

            return {
                "status": "APPROVED",
                "reason": "Strategy passed governance"
            }


        if score >= 60:

            return {
                "status": "REVIEW",
                "reason": "Needs evaluation"
            }


        return {
            "status": "REJECTED",
            "reason": "Low strategy quality"
        }