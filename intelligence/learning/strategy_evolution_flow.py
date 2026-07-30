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


        performance = self.performance_analyzer.analyze(
            history
        )


        governance_evolution = (
            self.governance_evolution.evaluate(
                {
                    "status": "STABLE",
                    "confidence": 10
                }
            )
        )


        governance_gate = (
            self.governance_gate.evaluate(
                {
                    "status": "APPROVED",
                    "confidence": 10
                }
            )
        )


        governance_result = {
            "approved": governance_gate["approved"],
            "gate": governance_gate,
            "evolution": governance_evolution
        }



        if not governance_gate["approved"]:


            return {
                "strategy": strategy,
                "performance": performance,
                "governance": governance_result,
                "evolution": {
                    "action": "BLOCKED",
                    "reason": governance_gate["reason"]
                }
            }



        if (
            governance_evolution["decision"]
            != "ALLOW_EVOLUTION"
        ):


            return {
                "strategy": strategy,
                "performance": performance,
                "governance": governance_result,
                "evolution": {
                    "action": governance_evolution["decision"],
                    "reason": governance_evolution["reason"]
                }
            }



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
            "governance": governance_result,
            "evolution": decision
        }