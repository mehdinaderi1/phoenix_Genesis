from intelligence.learning.strategy_optimizer import StrategyScore


class StrategyImprovementEngine:
    """
    Improves strategies based on historical performance.
    """


    def improve(
        self,
        strategy,
        current_score,
        performance_records
    ):

        score = current_score


        wins = 0
        losses = 0


        for record in performance_records:

            if record.success:
                wins += 1

            else:
                losses += 1


        if wins > losses:

            score += 5

        elif losses > wins:

            score -= 5


        score = max(
            0,
            min(
                100,
                score
            )
        )


        return StrategyScore(
            strategy=strategy,
            score=score
        )