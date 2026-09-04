class StrategyEvolutionDecision:

    def __init__(
        self,
        evolution_engine=None
    ):
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

            return {
                "action": "EVOLVE",
                "strategy": strategy,
                "parent": strategy,
                "reason": "performance can improve"
            }

        return {
            "action": "RETIRE",
            "strategy": strategy,
            "reason": "poor performance"
        }