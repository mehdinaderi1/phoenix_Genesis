"""
Lifecycle Evolution Flow

Connects lifecycle decisions with evolution execution
and persists evolution results.
"""

from typing import Any, Optional


class LifecycleEvolutionFlow:
    """
    End-to-end lifecycle evolution coordinator.

    Flow:

    Strategy
        ↓
    LifecycleDecisionEngine
        ↓
    LifecycleEvolutionController
        ↓
    Evolution Result
        ↓
    LifecycleEvolutionRepository
        ↓
    History
    """

    def __init__(
        self,
        lifecycle_decision_engine: Any,
        evolution_controller: Any,
        lifecycle_history: Optional[Any] = None,
        evolution_repository: Optional[Any] = None
    ):
        self.lifecycle_decision_engine = lifecycle_decision_engine
        self.evolution_controller = evolution_controller
        self.lifecycle_history = lifecycle_history
        self.evolution_repository = evolution_repository


    def execute(self, strategy):

        decision = self.lifecycle_decision_engine.decide(
            strategy
        )

        result = self.evolution_controller.execute(
            decision,
            strategy
        )

        if self.lifecycle_history:
            self.lifecycle_history.add(
                result
            )

        if self.evolution_repository:
            self.evolution_repository.save(
                result
            )

        return result