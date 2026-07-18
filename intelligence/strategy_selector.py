class StrategySelector:


    def __init__(
        self,
        strategy_recall,
        strategy_ranking
    ):

        self.strategy_recall = strategy_recall

        self.strategy_ranking = strategy_ranking



    def select(
        self,
        regime,
        signal,
        risk
    ):

        strategies = self.strategy_recall.recall(
            regime,
            signal,
            risk
        )


        ranked = self.strategy_ranking.rank(
            strategies
        )


        if not ranked:

            return None


        return ranked[0]