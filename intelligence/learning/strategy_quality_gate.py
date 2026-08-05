class StrategyQualityGate:

    def __init__(
        self,
        min_score=60,
        min_samples=1,
        min_success_rate=0.5
    ):
        self.min_score = min_score
        self.min_samples = min_samples
        self.min_success_rate = min_success_rate


    def validate(self, strategy):

        if strategy.get("score", 0) < self.min_score:
            return False

        if strategy.get("samples", 0) < self.min_samples:
            return False

        if strategy.get("success_rate", 0) < self.min_success_rate:
            return False

        return True