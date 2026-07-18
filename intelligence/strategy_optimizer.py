class StrategyOptimizer:
    """
    Selects the best strategy
    from available learned strategies.
    """


    def optimize(self, strategies):

        if not strategies:

            return None


        best_strategy = None

        best_score = -1


        for strategy in strategies:

            score = strategy.get(
                "score",
                0
            )


            success_rate = strategy.get(
                "success_rate",
                0
            )


            quality = (
                score * success_rate
            )


            if quality > best_score:

                best_score = quality

                best_strategy = strategy


        return best_strategy