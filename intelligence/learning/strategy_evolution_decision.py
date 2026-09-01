from intelligence.learning.strategy_evolution_engine import (
    StrategyEvolutionEngine
)


class StrategyEvolutionDecision:

    def __init__(
        self,
        evolution_engine=None
    ):

        if evolution_engine is None:
            evolution_engine = StrategyEvolutionEngine()

        self.evolution_engine = evolution_engine


    def evaluate(
        self,
        strategy,
        score,
        history=None
    ):

        if score >= 85:

            return {
                "action": "KEEP",
                "strategy": strategy,
                "reason": "high performance"
            }


        if score >= 70:

            evolved = self.evolution_engine.evolve(
                strategy,
                score
            )

            return {
                "action": "EVOLVE",
                "strategy": evolved["strategy"],
                "parent": evolved["parent"],
                "reason": "performance can improve",
                "generation": evolved["generation"]
            }


        return {
            "action": "RETIRE",
            "strategy": strategy,
            "reason": "poor performance"
        }