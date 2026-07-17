class StrategyLearner:
    """
    Converts analyzed experience patterns
    into reusable strategy knowledge.
    """

    def __init__(self, strategy_memory):

        self.strategy_memory = strategy_memory


    def learn(self, patterns):

        learned = []

        for pattern in patterns:

            regime, signal, risk = (
                pattern["pattern"]
            )

            strategy_record = {

                "strategy": (
                    f"{regime}_{signal}_{risk}"
                ),

                "regime": regime,

                "signal": signal,

                "risk": risk,

                "samples": (
                    pattern["samples"]
                ),

                "success_rate": (
                    pattern["success_rate"]
                ),

                "score": (
                    pattern["avg_score"]
                )
            }


            self.strategy_memory.store(
                strategy_record
            )

            learned.append(
                strategy_record
            )


        return learned