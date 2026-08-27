from intelligence.strategy_ranking_builder import StrategyRankingBuilder


class StrategyRankRecord(dict):
    """
    Backward compatible ranking item.

    Supports:
    - dict access:
        item["strategy"]

    - object access:
        item.strategy_name
    """


    @property
    def strategy_name(self):

        return self.get(
            "strategy"
        )



class StrategyRanker:
    """
    Learning strategy ranker.

    Contract:
    - rank() -> list[StrategyRankRecord]
    - rank_with_result() -> StrategyRankingResult
    - best() -> StrategyRankRecord
    """


    def __init__(self):

        self.builder = StrategyRankingBuilder()



    def _rank_records(
        self,
        strategies
    ):

        if not strategies:

            return []


        ranked = sorted(
            strategies,
            key=self._score,
            reverse=True
        )


        return [
            StrategyRankRecord(strategy)
            for strategy in ranked
        ]



    def rank(
        self,
        strategies
    ):

        return self._rank_records(
            strategies
        )



    def rank_with_result(
        self,
        strategies,
        market_context=None
    ):

        ranked = self._rank_records(
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