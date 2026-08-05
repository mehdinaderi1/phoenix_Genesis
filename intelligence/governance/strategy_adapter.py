from intelligence.learning.strategy_version import StrategyVersion


class StrategyAdapter:


    def convert(
        self,
        strategy
    ):

        if strategy is None:

            return None


        if isinstance(
            strategy,
            StrategyVersion
        ):

            return strategy


        name = self._get_value(
            strategy,
            "name",
            "unknown_strategy"
        )


        score = self._get_value(
            strategy,
            "score",
            0
        )


        success_rate = self._get_value(
            strategy,
            "success_rate",
            0
        )


        return StrategyVersion(

            name=name,

            version=self._get_value(
                strategy,
                "version",
                "v1"
            ),

            generation=self._get_value(
                strategy,
                "generation",
                1
            ),

            parent_strategy=self._get_value(
                strategy,
                "parent_strategy",
                None
            ),

            score=score,

            success_rate=success_rate,

            status=self._get_value(
                strategy,
                "status",
                "ACTIVE"
            )

        )



    def _get_value(
        self,
        obj,
        key,
        default
    ):

        if isinstance(obj, dict):

            return obj.get(
                key,
                default
            )


        return getattr(
            obj,
            key,
            default
        )