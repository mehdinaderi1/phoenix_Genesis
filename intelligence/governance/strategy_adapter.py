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

            score=score,

            success_rate=success_rate

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