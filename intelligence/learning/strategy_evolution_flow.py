from intelligence.learning.strategy_performance import (
    StrategyPerformanceAnalyzer
)

from intelligence.learning.strategy_evolution_decision import (
    StrategyEvolutionDecision
)

from intelligence.governance.governance_evolution import (
    GovernanceEvolution
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

from intelligence.governance.governance_recall import (
    GovernanceRecall
)

from intelligence.governance.governance_intelligence import (
    GovernanceIntelligence
)


class StrategyEvolutionFlow:
    """
    Strategy Evolution Orchestration Layer.

    Responsibilities:
    - Analyze strategy performance
    - Apply governance validation
    - Execute evolution decision
    - Store evolution memory

    Dependency construction is only fallback.
    Production dependencies should be injected
    through IntelligenceComponents.
    """


    def __init__(
        self,
        performance_analyzer=None,
        evolution_decision=None,
        governance_evolution=None,
        governance_gate=None,
        governance_memory=None,
        governance_recall_flow=None,
        governance_intelligent_gate=None,
        evolution_memory=None
    ):

        # ---------------------------------------------
        # Performance Intelligence
        # ---------------------------------------------

        if performance_analyzer is None:
            performance_analyzer = (
                StrategyPerformanceAnalyzer()
            )

        self.performance_analyzer = (
            performance_analyzer
        )


        # ---------------------------------------------
        # Evolution Decision
        # ---------------------------------------------

        if evolution_decision is None:
            evolution_decision = (
                StrategyEvolutionDecision()
            )

        self.evolution_decision = (
            evolution_decision
        )


        # ---------------------------------------------
        # Governance Intelligence
        # ---------------------------------------------

        if governance_evolution is None:
            governance_evolution = (
                GovernanceEvolution()
            )

        self.governance_evolution = (
            governance_evolution
        )


        if governance_gate is None:
            governance_gate = (
                GovernanceGate()
            )

        self.governance_gate = (
            governance_gate
        )


        if governance_memory is None:
            governance_memory = (
                GovernanceMemory()
            )

        self.governance_memory = (
            governance_memory
        )


        if governance_recall_flow is None:

            governance_recall_flow = (
                GovernanceRecallFlow(
                    memory=self.governance_memory
                )
            )

        self.governance_recall_flow = (
            governance_recall_flow
        )


        if governance_intelligent_gate is None:

            governance_recall = (
                GovernanceRecall(
                    self.governance_memory
                )
            )

            governance_intelligence = (
                GovernanceIntelligence(
                    governance_recall
                )
            )

            governance_intelligent_gate = (
                GovernanceIntelligentGate(
                    governance_intelligence
                )
            )

        self.governance_intelligent_gate = (
            governance_intelligent_gate
        )


        # ---------------------------------------------
        # Evolution Memory
        # ---------------------------------------------

        if evolution_memory is None:
            evolution_memory = (
                GovernanceEvolutionMemory()
            )

        self.evolution_memory = (
            evolution_memory
        )


    def evaluate(
        self,
        strategy,
        history
    ):

        # ---------------------------------------------
        # 1. Performance Analysis
        # ---------------------------------------------

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


        # ---------------------------------------------
        # 2. Governance Recall
        # ---------------------------------------------

        governance_recall = (
            self.governance_recall_flow.analyze(
                strategy
            )
        )


        # ---------------------------------------------
        # 3. Governance Gates
        # ---------------------------------------------

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

            "approved": (
                governance_gate.get(
                    "approved",
                    True
                )
            ),

            "gate": governance_gate,

            "intelligent_gate": intelligent_gate,

            "evolution": (
                self.governance_evolution.evaluate(
                    {
                        "status": "STABLE",
                        "confidence": score
                    }
                )
            )
        }


        # ---------------------------------------------
        # 4. Governance Rejection
        # ---------------------------------------------

        if (
            not governance["approved"]
            or not intelligent_gate["approved"]
        ):

            return {

                "strategy": strategy,

                "performance": performance,

                "governance": governance,

                "governance_recall": (
                    governance_recall
                ),

                "evolution": {

                    "action": "BLOCKED",

                    "reason": (
                        "Governance rejected"
                    )
                },

                "governance_memory_count": (
                    self.evolution_memory.count()
                )
            }


        # ---------------------------------------------
        # 5. Evolution Decision
        # ---------------------------------------------

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


        # ---------------------------------------------
        # 6. Final Result
        # ---------------------------------------------

        return {

            "strategy": strategy,

            "performance": performance,

            "governance": governance,

            "governance_recall": (
                governance_recall
            ),

            "evolution": decision,

            "governance_memory_count": (
                self.evolution_memory.count()
            )
        }