from intelligence.strategy_ranking_builder import StrategyRankingBuilder


class StrategyRanker:
    """
    Ranks learned strategies based on performance.
    """


    def __init__(self):

        self.builder = StrategyRankingBuilder()



    def rank(
        self,
        strategies
    ):

        if not strategies:

            return []


        return sorted(
            strategies,
            key=self._score,
            reverse=True
        )



    def rank_with_result(
        self,
        strategies,
        market_context=None
    ):

        ranked = self.rank(
            strategies
        )


        return self.builder.build(
            ranked,
            market_context
        )



    def best(
        self,
        strategies
    ):

        ranked = self.rank(
            strategies
        )


        if not ranked:

            return None


        return ranked[0]



    def _score(
        self,
        strategy
    ):

        status = strategy.get(
            "status",
            "ACTIVE"
        )


        if status != "ACTIVE":

            return -1


        score = strategy.get(
            "score",
            0
        )


        success_rate = strategy.get(
            "success_rate",
            0
        )


        samples = strategy.get(
            "samples",
            0
        )


        return (
            score * 0.5
            +
            success_rate * 0.4
            +
            min(samples, 100) * 0.1
        )
