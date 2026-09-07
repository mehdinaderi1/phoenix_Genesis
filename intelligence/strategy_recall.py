class StrategyRecall:
    """
    Retrieves previous learned strategies
    based on current market conditions.
    """


    def __init__(
        self,
        strategy_memory
    ):

        self.strategy_memory = strategy_memory



    def _normalize_regime(
        self,
        regime
    ):

        regime = str(regime).upper()


        mapping = {

            "TRENDING_BULLISH":
                "BULLISH",

            "TRENDING_BEARISH":
                "BEARISH"

        }


        return mapping.get(
            regime,
            regime
        )



    def recall(
        self,
        regime,
        signal,
        risk
    ):

        normalized_regime = (
            self._normalize_regime(
                regime
            )
        )


        strategies = (
            self.strategy_memory
            .find_by_pattern(
                normalized_regime,
                signal,
                risk
            )
        )

        if not strategies and normalized_regime != regime:

            strategies = (
                self.strategy_memory
                .find_by_pattern(
                    regime,
                    signal,
                    risk
                )
            )


        return [
            strategy
            for strategy in strategies
            if strategy.get("status")
            not in (
                "RETIRED",
                "CANDIDATE"
            )
        ]



    def best(
        self,
        regime,
        signal,
        risk
    ):

        strategies = self.recall(
            regime,
            signal,
            risk
        )


        if not strategies:

            return None


        return max(
            strategies,
            key=lambda x: x.get(
                "score",
                0
            )
        )