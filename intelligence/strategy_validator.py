class StrategyValidator:

    def validate(self, strategy):

        if strategy is None:
            return {
                "valid": False,
                "reason": "NO_STRATEGY",
                "confidence": 0
            }


        if strategy.get("status") != "ACTIVE":
            return {
                "valid": False,
                "reason": "NOT_ACTIVE",
                "confidence": 0
            }


        score = strategy.get(
            "score",
            0
        )

        success_rate = strategy.get(
            "success_rate",
            0
        )


        confidence = (
            score * 0.6
            +
            success_rate * 100 * 0.4
        )


        return {
            "valid": confidence >= 70,
            "confidence": confidence,
            "reason": "VALIDATED"
        }