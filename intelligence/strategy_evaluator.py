class StrategyEvaluator:
    """
    Evaluates learned strategies
    before storing them as knowledge.
    """

    def __init__(
        self,
        min_samples=5,
        min_success_rate=0.6
    ):

        self.min_samples = min_samples

        self.min_success_rate = min_success_rate


    def evaluate(
        self,
        strategy
    ):

        samples = strategy.get(
            "samples",
            0
        )

        success_rate = strategy.get(
            "success_rate",
            0
        )


        if samples < self.min_samples:

            return {
                "accepted": False,
                "reason": "Not enough samples"
            }


        if success_rate < self.min_success_rate:

            return {
                "accepted": False,
                "reason": "Low success rate"
            }


        return {
            "accepted": True,
            "reason": "Strategy meets quality requirements"
        }