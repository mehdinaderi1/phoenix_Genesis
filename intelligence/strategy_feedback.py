from intelligence.performance_record import PerformanceRecord


class StrategyFeedback:


    def create_record(
        self,
        strategy,
        feedback
    ):

        return PerformanceRecord(

            strategy=strategy,

            profit_loss=(
                feedback["score"] / 100
            ),

            success=(
                feedback["result"]
                == "SUCCESS"
            )
        )