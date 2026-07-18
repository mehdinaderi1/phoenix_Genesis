class StrategyUpdate:


    def __init__(
        self,
        strategy_memory,
        quality_gate=None
    ):

        self.strategy_memory = strategy_memory
        self.quality_gate = quality_gate



    def update(
        self,
        strategy_score,
        context=None
    ):

        if context is None:

            context = {}


        record = {

            "strategy": strategy_score.strategy,

            "score": strategy_score.score,

            "samples": getattr(
                strategy_score,
                "samples",
                0
            ),

            "success_rate": getattr(
                strategy_score,
                "success_rate",
                0
            ),

            "regime": context.get("regime"),

            "signal": context.get("signal"),

            "risk": context.get("risk")

        }


        if self.quality_gate:

            accepted = self.quality_gate.validate(record)

            if not accepted:

                return {
                    "updated": False,
                    "reason": "quality_gate_failed",
                    "record": record
                }



        if context:

            self.strategy_memory.store(record)

        else:

            updated = self.strategy_memory.update_strategy(record)

            if not updated:

                self.strategy_memory.store(record)


        return {
            "updated": True,
            "record": record,
            **record
        }