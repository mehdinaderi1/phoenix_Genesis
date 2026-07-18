class StrategyUpdate:


    def __init__(self, strategy_memory):

        self.strategy_memory = strategy_memory



    def update(
        self,
        strategy_score
    ):

        record = {

            "strategy": strategy_score.strategy,

            "score": strategy_score.score

        }


        existing = False


        for item in self.strategy_memory.records:

            if (
                item.get("strategy")
                == record["strategy"]
            ):

                existing = True

                break



        if existing:

            updated = self.strategy_memory.update_strategy(
                record
            )

            if updated:

                return record


            return None



        self.strategy_memory.store(
            record
        )


        return record