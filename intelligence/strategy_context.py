class StrategyContext:
    """
    Builds historical strategy insight
    from recalled strategies.
    """


    def __init__(
        self,
        strategy_recall
    ):

        self.strategy_recall = strategy_recall



    def analyze(
        self,
        regime,
        signal,
        risk
    ):

        strategy = self.strategy_recall.best(
            regime,
            signal,
            risk
        )


        if not strategy:

            return None


        return {

            "strategy": strategy.get(
                "strategy"
            ),

            "score": strategy.get(
                "score",
                0
            ),

            "message":
                "Previous similar conditions performed well"
        }