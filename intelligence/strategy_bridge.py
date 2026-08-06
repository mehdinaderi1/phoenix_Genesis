from intelligence.governance.strategy_governor import StrategyGovernor
from intelligence.learning.strategy_version import StrategyVersion


class StrategyBridge:


    def __init__(
        self,
        governor=None
    ):

        self.governor = governor or StrategyGovernor()



    def _to_strategy_version(
        self,
        record
    ):

        if isinstance(record, StrategyVersion):

            return record


        return StrategyVersion(

            name=record.get(
                "name",
                record.get("strategy")
            ),

            version=record.get(
                "version",
                "v1"
            ),

            generation=record.get(
                "generation",
                1
            ),

            score=record.get(
                "score",
                0.0
            ),

            success_rate=record.get(
                "success_rate",
                0.0
            ),

            status=record.get(
                "status",
                "ACTIVE"
            )
        )



    def get_best_strategy(
        self,
        strategies
    ):

        strategy_versions = [

            self._to_strategy_version(s)

            for s in strategies

        ]


        champion = self.governor.select_champion(
            strategy_versions
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
        context,
        strategies
    ):

        champion = self.get_best_strategy(
            strategies
        )


        enriched = dict(context)


        if champion:

            enriched["champion_strategy"] = champion


        return enriched