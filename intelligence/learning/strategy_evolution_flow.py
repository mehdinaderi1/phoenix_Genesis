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

from intelligence.governance.governance_intelligent_gate import (
    GovernanceIntelligentGate
)

from intelligence.governance.governance_evolution_memory import (
    GovernanceEvolutionMemory
)

from intelligence.governance.governance_memory import (
    GovernanceMemory
)

from intelligence.governance.governance_recall_flow import (
    GovernanceRecallFlow
)



class StrategyEvolutionFlow:


    def __init__(
        self,
        performance_analyzer=None,
        evolution_decision=None,
        governance_evolution=None,
        governance_service=None,
        governance_gate=None,
        governance_memory=None,
        governance_recall_flow=None,
        governance_intelligent_gate=None,
        evolution_memory=None
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


        self.governance_memory = (
            governance_memory
            or GovernanceMemory()
        )


        self.governance_recall_flow = (
            governance_recall_flow
            or GovernanceRecallFlow(
                self.governance_memory
            )
        )


        self.governance_intelligent_gate = (
            governance_intelligent_gate
            or GovernanceIntelligentGate()
        )


        self.evolution_memory = (
            evolution_memory
            or GovernanceEvolutionMemory()
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


        governance_recall = (
            self.governance_recall_flow.analyze(
                strategy
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


        intelligent_gate = (
            self.governance_intelligent_gate.evaluate(
                strategy
            )
        )


        governance = {

            "approved":
                governance_gate.get(
                    "approved",
                    True
                ),

            "gate":
                governance_gate,

            "intelligent_gate":
                intelligent_gate,

            "evolution":
                self.governance_evolution.evaluate(
                    {
                        "status": "STABLE",
                        "confidence": score
                    }
                )
        }



        if (
            not governance["approved"]
            or not intelligent_gate["approved"]
        ):


            return {

                "strategy": strategy,

                "performance": performance,

                "governance": governance,

                "governance_recall":
                    governance_recall,

                "evolution": {

                    "action": "BLOCKED",

                    "reason":
                        "Governance rejected"

                },

                "governance_memory_count":
                    self.evolution_memory.count()

            }



        decision = (
            self.evolution_decision.evaluate(
                strategy,
                score,
                history
            )
        )



        self.evolution_memory.store(
            strategy,
            decision["action"],
            score
        )


        return {

            "strategy": strategy,

            "performance": performance,

            "governance": governance,

            "governance_recall":
                governance_recall,

            "evolution": decision,

            "governance_memory_count":
                self.evolution_memory.count()

        }