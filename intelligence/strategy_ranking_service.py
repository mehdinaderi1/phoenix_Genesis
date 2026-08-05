from intelligence.strategy_ranking_builder import StrategyRankingBuilder


class StrategyRankingService:


    def __init__(
        self,
        ranker,
        builder=None
    ):

        self.ranker = ranker

        self.builder = (
            builder
            if builder
            else StrategyRankingBuilder()
        )


    def rank(
        self,
        strategies,
        market_context=None
    ):

        ranked = self.ranker.rank(
            strategies
        )


        return self.builder.build(
            ranked,
            market_context
        )