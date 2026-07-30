from intelligence.governance.strategy_governor import StrategyGovernor


class StrategyBridge:


    def __init__(
        self,
        governor=None
    ):

        self.governor = governor or StrategyGovernor()



    def get_best_strategy(
        self,
        strategies
    ):

        champion = self.governor.select_champion(
            strategies
        )


        if champion is None:

            return None


        return {

            "name": champion.name,

            "version": champion.version,

            "generation": champion.generation,

            "score": champion.score,

            "success_rate": champion.success_rate,

            "status": champion.status

        }



    def enrich_market_context(
        self,
        market_context,
        strategies
    ):

        strategy = self.get_best_strategy(
            strategies
        )


        if strategy is None:

            return market_context


        market_context["champion_strategy"] = strategy


        return market_context