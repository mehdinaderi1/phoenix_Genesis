from intelligence.learning.strategy_evolution_history import (
    StrategyEvolutionHistory
)


class StrategyEvolutionAnalytics:

    def __init__(
        self,
        history: StrategyEvolutionHistory
    ):
        self.history = history

    def summary(self):

        records = self.history.all()

        if not records:

            return {
                "total": 0,
                "improved": 0,
                "retired": 0,
                "kept": 0,
                "average_score": 0.0,
                "average_success_rate": 0.0
            }

        total = len(records)

        improved = sum(
            1 for r in records
            if r.decision == "IMPROVE"
        )

        retired = sum(
            1 for r in records
            if r.decision == "RETIRE"
        )

        kept = sum(
            1 for r in records
            if r.decision == "KEEP"
        )

        avg_score = (
            sum(r.score for r in records)
            / total
        )

        avg_success = (
            sum(r.success_rate for r in records)
            / total
        )

        return {

            "total": total,

            "improved": improved,

            "retired": retired,

            "kept": kept,

            "average_score": round(
                avg_score,
                2
            ),

            "average_success_rate": round(
                avg_success,
                2
            )
        }