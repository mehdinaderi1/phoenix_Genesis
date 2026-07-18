from intelligence.learning.self_improvement import SelfImprovement
from intelligence.learning.strategy_optimizer import StrategyOptimizer


class StrategyImprovementEngine:
    """
    Connects performance analysis
    with strategy optimization.
    """


    def __init__(self):

        self.self_improvement = SelfImprovement()

        self.optimizer = StrategyOptimizer()


    def improve(
        self,
        strategy,
        current_score,
        performance_records
    ):

        report = self.self_improvement.analyze(
            performance_records
        )


        result = self.optimizer.optimize(
            strategy,
            current_score,
            report
        )


        return result