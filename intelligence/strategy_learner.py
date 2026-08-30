from intelligence.strategy_evaluator import StrategyEvaluator


class StrategyLearner:
    """
    Converts analyzed experience patterns
    into reusable strategy knowledge.
    """

    def __init__(
        self,
        strategy_memory,
        evaluator=None
    ):

        self.strategy_memory = strategy_memory

        self.evaluator = (
            evaluator
            if evaluator
            else StrategyEvaluator()
        )


    def _resolve_pattern_context(
        self,
        raw_pattern,
        pattern
    ):

        if isinstance(raw_pattern, tuple):

            return raw_pattern

        if isinstance(raw_pattern, str):

            if (
                pattern.get("strategy")
                and pattern.get("regime") is not None
                and pattern.get("signal") is not None
                and pattern.get("risk") is not None
            ):

                return (
                    pattern.get("regime"),
                    pattern.get("signal"),
                    pattern.get("risk")
                )

            parts = raw_pattern.split("_")

            if len(parts) == 3:

                return tuple(parts)

        return None


    def _build_strategy_record(
        self,
        strategy_name,
        regime,
        signal,
        risk,
        strategy_data
    ):

        strategy_record = {

            "strategy": strategy_name,

            "regime": regime,

            "signal": signal,

            "action": signal,

            "risk": risk,

            "samples": strategy_data.get(
                "samples",
                0
            ),

            "success_rate": strategy_data.get(
                "success_rate",
                0
            ),

            "score": strategy_data.get(
                "avg_score",
                0
            ),

            "status": "CANDIDATE"
        }

        return strategy_record


    def learn(
        self,
        patterns
    ):

        learned = []


        for pattern in patterns:

            raw_pattern = pattern.get(
                "pattern"
            )


            context = self._resolve_pattern_context(
                raw_pattern,
                pattern
            )


            if context is None:

                continue


            regime, signal, risk = context


            strategies = pattern.get(
                "strategies"
            )


            if strategies:

                strategy_items = (
                    strategies.items()
                )

            else:

                strategy_name = (
                    pattern.get("strategy")
                    or
                    f"{regime}_{signal}_{risk}"
                )

                strategy_items = [
                    (
                        strategy_name,
                        {
                            "samples":
                                pattern.get(
                                    "samples",
                                    0
                                ),

                            "success_rate":
                                pattern.get(
                                    "success_rate",
                                    0
                                ),

                            "avg_score":
                                pattern.get(
                                    "avg_score",
                                    0
                                )
                        }
                    )
                ]


            for strategy_name, strategy_data in strategy_items:

                strategy_record = (
                    self._build_strategy_record(
                        strategy_name,
                        regime,
                        signal,
                        risk,
                        strategy_data
                    )
                )


                evaluation = (
                    self.evaluator.evaluate(
                        strategy_record
                    )
                )


                strategy_record["evaluation"] = (
                    evaluation
                )


                if evaluation["accepted"]:

                    strategy_record["status"] = (
                        "ACTIVE"
                    )

                    self.strategy_memory.store(
                        strategy_record
                    )

                    learned.append(
                        strategy_record
                    )


        return learned
