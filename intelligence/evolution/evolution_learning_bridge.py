from intelligence.learning.strategy_evolution_insight import (
    StrategyEvolutionInsight
)


class EvolutionLearningBridge:

    def __init__(
        self,
        analytics,
        insight=None
    ):

        self.analytics = analytics

        self.insight = (
            insight
            or StrategyEvolutionInsight()
        )


    def evaluate(
        self,
        old_strategy,
        new_strategy,
        performance
    ):

        insight = self.insight.analyze(

            old_strategy,

            new_strategy,

            performance

        )


        return {

            "insight": insight,

            "learning": insight.learning,

            "confidence": insight.confidence,

            "reason": insight.reason,

            "improvement": insight.improvement

        }