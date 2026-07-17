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


    def learn(self, patterns):

        learned = []


        for pattern in patterns:

            raw_pattern = pattern["pattern"]


            if isinstance(raw_pattern, tuple):

                regime, signal, risk = raw_pattern

                pattern_name = (
                    f"{regime}_{signal}_{risk}"
                )


            elif isinstance(raw_pattern, str):

                pattern_name = raw_pattern

                parts = pattern_name.split("_")

                if len(parts) != 3:
                    continue

                regime, signal, risk = parts


            else:
                continue


            strategy_record = {

                "strategy": pattern_name,

                "regime": regime,

                "signal": signal,

                "risk": risk,

                "samples": pattern["samples"],

                "success_rate": pattern["success_rate"],

                "score": pattern["avg_score"]

            }


            evaluation = self.evaluator.evaluate(
                strategy_record
            )


            strategy_record["evaluation"] = evaluation


            if evaluation["accepted"]:

                self.strategy_memory.store(
                    strategy_record
                )

                learned.append(
                    strategy_record
                )


        return learned