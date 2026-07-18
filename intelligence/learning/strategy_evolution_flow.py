from intelligence.learning.strategy_performance import (
    StrategyPerformanceAnalyzer
)

from intelligence.learning.strategy_evolution_decision import (
    StrategyEvolutionDecision
)


class StrategyEvolutionFlow:

    def __init__(
        self,
        performance_analyzer=None,
        evolution_decision=None
    ):

        self.performance_analyzer = (
            performance_analyzer
            or StrategyPerformanceAnalyzer()
        )

        self.evolution_decision = (
            evolution_decision
            or StrategyEvolutionDecision()
        )


    def evaluate(
        self,
        strategy,
        history
    ):

        performance = self.performance_analyzer.analyze(
            history
        )


        score = performance.get(
            "score",
            performance.get(
                "average_score",
                0
            )
        )


        decision = self.evolution_decision.evaluate(
            strategy,
            score,
            history
        )


        return {
            "strategy": strategy,
            "performance": performance,
            "evolution": decision
        }