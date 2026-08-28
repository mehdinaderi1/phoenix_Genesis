from intelligence.outcome_record import OutcomeRecord
from intelligence.performance_record import PerformanceRecord


class DecisionOutcomeBridge:

    def __init__(
        self,
        outcome_memory,
        performance_feedback,
        strategy_performance_memory,
        performance_learning=None

    ):

        self.outcome_memory = outcome_memory

        self.performance_feedback = (
            performance_feedback
        )

        self.strategy_performance_memory = (
            strategy_performance_memory
        )

        self.performance_learning = (
            performance_learning
        )



    def _resolve_strategy(
        self,
        decision
    ):

        champion_strategy = getattr(
            decision,
            "champion_strategy",
            None
        )

        if champion_strategy:

            return champion_strategy.get(
                "name"
            )


        strategy = getattr(
            decision,
            "strategy",
            None
        )

        if strategy:

            return strategy.get(
                "name"
            )


        metadata = getattr(
            decision,
            "metadata",
            {}
        )

        champion_strategy = metadata.get(
            "champion_strategy"
        )

        if champion_strategy:

            return champion_strategy.get(
                "name"
            )


        return None


    def process(
        self,
        decision,
        entry_price,
        exit_price,
        strategy=None
    ):

        outcome = OutcomeRecord(
            decision=decision,
            entry_price=entry_price,
            exit_price=exit_price
        )


        self.outcome_memory.save_outcome(
            outcome
        )


        feedback = (
            self.performance_feedback.evaluate(
                outcome
            )
        )


        resolved_strategy = (
            strategy
            if strategy is not None
            else self._resolve_strategy(decision)
        )


        performance = None
        performance_learning = None


        if resolved_strategy:

            performance = PerformanceRecord(

                strategy=resolved_strategy,

                profit_loss=(
                    exit_price - entry_price
                ),

                success=(
                    feedback["result"]
                    == "SUCCESS"
                )
            )


            self.strategy_performance_memory.save_performance(
                performance
            )


            if self.performance_learning:

                performance_learning = (
                    self.performance_learning.process(
                        performance,
                        decision
                    )
                )


        return {

            "result": feedback["result"],

            "score": feedback["score"],

            "feedback": feedback,

            "performance": performance,

            "performance_learning": (
                performance_learning
            )
        }
