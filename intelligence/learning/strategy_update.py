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


        self.strategy_memory.store(
            record
        )


        return record