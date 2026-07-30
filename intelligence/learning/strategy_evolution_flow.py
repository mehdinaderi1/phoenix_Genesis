from intelligence.learning.strategy_performance import (
    StrategyPerformanceAnalyzer
)

from intelligence.learning.strategy_evolution_decision import (
    StrategyEvolutionDecision
)

from intelligence.governance.governance_evolution import (
    GovernanceEvolution
)

from intelligence.governance.governance_service import (
    GovernanceService
)

from intelligence.governance.governance_gate import (
    GovernanceGate
)


class StrategyEvolutionFlow:


    def __init__(
        self,
        performance_analyzer=None,
        evolution_decision=None,
        governance_evolution=None,
        governance_service=None,
        governance_gate=None
    ):


        self.performance_analyzer = (
            performance_analyzer
            or StrategyPerformanceAnalyzer()
        )


        self.evolution_decision = (
            evolution_decision
            or StrategyEvolutionDecision()
        )


        self.governance_evolution = (
            governance_evolution
            or GovernanceEvolution()
        )


        self.governance_service = (
            governance_service
            or GovernanceService(
                None
            )
        )


        self.governance_gate = (
            governance_gate
            or GovernanceGate()
        )



    def evaluate(
        self,
        strategy,
        history
    ):


        performance = (
            self.performance_analyzer.analyze(
                history
            )
        )


        score = performance.get(
            "score",
            performance.get(
                "average_score",
                0
            )
        )


        governance_gate = (
            self.governance_gate.evaluate(
                {
                    "status": "APPROVED",
                    "confidence": score
                }
            )
        )


        governance_evolution = (
            self.governance_evolution.evaluate(
                {
                    "status": "STABLE",
                    "confidence": score
                }
            )
        )


        governance = {
            "approved": governance_gate.get(
                "approved",
                True
            ),
            "gate": governance_gate,
            "evolution": governance_evolution
        }



        if not governance["approved"]:

            return {
                "strategy": strategy,
                "performance": performance,
                "governance": governance,
                "evolution": {
                    "action": "BLOCKED",
                    "reason": governance_gate.get(
                        "reason",
                        "Governance rejected"
                    )
                }
            }



        decision = self.evolution_decision.evaluate(
            strategy,
            score,
            history
        )


        return {
            "strategy": strategy,
            "performance": performance,
            "governance": governance,
            "evolution": decision
        }