from dataclasses import dataclass


@dataclass
class LifecycleEvolutionResult:
    action: str
    executed: bool
    strategy_version: str
    result: str


class LifecycleEvolutionController:

    def __init__(
        self,
        improvement_engine,
        evolution_engine,
        evaluator,
        strategy_memory
    ):
        self.improvement_engine = improvement_engine
        self.evolution_engine = evolution_engine
        self.evaluator = evaluator
        self.strategy_memory = strategy_memory


    def execute(self, decision, strategy):

        action = decision.action

        if action == "KEEP":
            return LifecycleEvolutionResult(
                action,
                True,
                strategy.version,
                "Strategy retained"
            )


        if action == "IMPROVE":
            improved = self.improvement_engine.improve(strategy)

            evolved = self.evolution_engine.evolve(
                improved
            )

            return LifecycleEvolutionResult(
                action,
                True,
                evolved.version,
                "Strategy improved"
            )


        if action == "ARCHIVE":

            self.strategy_memory.store(strategy)

            return LifecycleEvolutionResult(
                action,
                True,
                strategy.version,
                "Strategy archived"
            )


        if action == "EVALUATE":

            result = self.evaluator.evaluate(strategy)

            return LifecycleEvolutionResult(
                action,
                True,
                strategy.version,
                result
            )


        return LifecycleEvolutionResult(
            action,
            False,
            strategy.version,
            "Unknown lifecycle action"
        )