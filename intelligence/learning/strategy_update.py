class StrategyUpdate:


    def __init__(
        self,
        strategy_memory,
        quality_gate=None,
        strategy_history=None
    ):

        self.strategy_memory = strategy_memory
        self.quality_gate = quality_gate
        self.strategy_history = strategy_history



    def update(
        self,
        strategy_score,
        context=None
    ):

        if context is None:

            context = {}


        existing = None

        for item in self.strategy_memory.records:

            if item.get("strategy") == strategy_score.strategy:

                existing = item

                break



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

            "regime": context.get(
                "regime",
                existing.get("regime") if existing else None
            ),

            "signal": context.get(
                "signal",
                existing.get("signal") if existing else None
            ),

            "risk": context.get(
                "risk",
                existing.get("risk") if existing else None
            ),

            "status": (
                existing.get("status")
                if existing
                else "ACTIVE"
            )

        }



        if self.quality_gate:

            accepted = self.quality_gate.validate(
                record
            )

            if not accepted:

                self.strategy_memory.store(
                    record
                )

                return {
                    "updated": False,
                    "reason": "quality_gate_failed",
                    "record": record,
                    **record
                }



        if context:

            self.strategy_memory.store(
                record
            )

        else:

            updated = self.strategy_memory.update_strategy(
                record
            )

            if not updated:

                self.strategy_memory.store(
                    record
                )



        if self.strategy_history:

            self.strategy_history.add_record(

                strategy_score.strategy,

                strategy_score.score,

                getattr(
                    strategy_score,
                    "success_rate",
                    0
                ),

                getattr(
                    strategy_score,
                    "samples",
                    0
                )

            )



        return {

            "updated": True,

            "record": record,

            **record

        }