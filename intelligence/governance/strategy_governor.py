from intelligence.learning.strategy_version import StrategyVersion


class StrategyGovernor:


    def evaluate(
        self,
        strategy: StrategyVersion
    ):

        if strategy.score >= 80 and strategy.success_rate >= 0.7:

            strategy.activate()

            return "APPROVED"


        if strategy.score < 40 or strategy.success_rate < 0.3:

            strategy.archive()

            return "ARCHIVED"


        strategy.status = "REVIEW"

        return "REVIEW"



    def select_champion(
        self,
        strategies
    ):

        if not strategies:

            return None


        active_strategies = [

            s for s in strategies

            if s.status == "ACTIVE"

        ]


        if not active_strategies:

            return None


        return max(

            active_strategies,

            key=lambda x: x.score * x.success_rate

        )