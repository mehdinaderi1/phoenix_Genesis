"""
Lifecycle Evolution Intelligence Flow

Connects evolution context,
decision intelligence and evolution execution.
"""


class LifecycleEvolutionIntelligenceFlow:
    """
    Full intelligent lifecycle evolution pipeline.

    Flow:

    Strategy Metrics
        ↓
    Evolution Context
        ↓
    Evolution Decision
        ↓
    Evolution Controller
        ↓
    Result
    """

    def __init__(
        self,
        evolution_context,
        evolution_decision,
        evolution_controller,
        evolution_repository=None
    ):
        self.evolution_context = evolution_context
        self.evolution_decision = evolution_decision
        self.evolution_controller = evolution_controller
        self.evolution_repository = evolution_repository


    def execute(
        self,
        strategy,
        score
    ):

        context = self.evolution_context.build(
            strategy
        )

        decision = self.evolution_decision.decide(
            score,
            context
        )

        result = self.evolution_controller.execute(
            decision,
            strategy
        )

        if self.evolution_repository:
            self.evolution_repository.save(
                result
            )

        return result