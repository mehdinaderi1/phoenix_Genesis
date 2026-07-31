class StrategySelector:


    def __init__(
        self,
        strategy_recall,
        strategy_ranking,
        evolution_intelligence=None
    ):

        self.strategy_recall = strategy_recall

        self.strategy_ranking = strategy_ranking

        self.evolution_intelligence = evolution_intelligence



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


        champion = ranked[0]


        if self.evolution_intelligence:


            evolution_result = self.evolution_intelligence.analyze(
                ranked
            )


            if (
                evolution_result
                and evolution_result.get(
                    "available"
                )
            ):

                evolved_strategy = evolution_result.get(
                    "strategy"
                )


                if evolved_strategy:

                    champion = evolved_strategy



        return champion