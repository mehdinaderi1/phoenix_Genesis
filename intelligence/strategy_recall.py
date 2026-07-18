class StrategyRecall:
    """
    Retrieves previous learned strategies
    based on current market conditions.
    """


    def __init__(
        self,
        strategy_memory
    ):

        self.strategy_memory = strategy_memory



    def recall(
        self,
        regime,
        signal,
        risk
    ):

        return (
            self.strategy_memory
            .find_by_pattern(
                regime,
                signal,
                risk
            )
        )



    def best(
        self,
        regime,
        signal,
        risk
    ):

        strategies = self.recall(
            regime,
            signal,
            risk
        )


        if not strategies:

            return None


        return max(
            strategies,
            key=lambda x: x.get(
                "score",
                0
            )
        )