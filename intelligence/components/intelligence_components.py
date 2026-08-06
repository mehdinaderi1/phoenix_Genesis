from intelligence.reasoning import ReasoningEngine
from intelligence.regime_analyzer import RegimeAnalyzer
from intelligence.risk_analyzer import RiskAnalyzer

from intelligence.decision_engine import DecisionEngine
from intelligence.decision_validator import DecisionValidator
from intelligence.decision_memory import DecisionMemory
from intelligence.decision_quality import DecisionQualityAnalyzer
from intelligence.learning.strategy_ranker import StrategyRanker
from intelligence.learning.strategy_history import StrategyHistory
from intelligence.learning.strategy_performance import (
    StrategyPerformanceAnalyzer
)
from intelligence.strategy_memory import StrategyMemory
from intelligence.strategy_learner import StrategyLearner
from intelligence.strategy_recall import StrategyRecall
from intelligence.strategy_selector import StrategySelector
from intelligence.strategy_intelligence_adapter import (
    StrategyIntelligenceAdapter
)
from intelligence.strategy_intelligence_service import (
    StrategyIntelligenceService
)
from intelligence.strategy_context import StrategyContext
from intelligence.strategy_feedback import StrategyFeedback
from intelligence.learning.strategy_quality_gate import (
    StrategyQualityGate
)

from intelligence.learning.strategy_improvement_engine import (
    StrategyImprovementEngine
)

from intelligence.learning.strategy_update import StrategyUpdate

from intelligence.strategy_bridge import StrategyBridge

from intelligence.strategy_governance import StrategyGovernance

from intelligence.governance.governance_memory import (
    GovernanceMemory
)

from intelligence.governance.governance_feedback import (
    GovernanceFeedback
)

from intelligence.governance.governance_confidence import (
    GovernanceConfidence
)

from intelligence.evolution.evolution_history import (
    EvolutionHistory
)

from intelligence.evolution.evolution_recall import (
    EvolutionRecall
)

from intelligence.evolution.evolution_recall_analyzer import (
    EvolutionRecallAnalyzer
)

from intelligence.evolution.evolution_intelligence import (
    EvolutionIntelligence
)

from intelligence.evolution.self_evolution_controller import (
    SelfEvolutionController
)

from intelligence.evolution.evolution_execution import (
    EvolutionExecution
)

from intelligence.learning.strategy_evolution_engine import (
    StrategyEvolutionEngine
)

from intelligence.evolution.evolution_analytics import (
    EvolutionAnalytics
)

from intelligence.evolution.evolution_decision import (
    EvolutionDecision
)

from intelligence.evolution.rollback_engine import (
    RollbackEngine
)

from intelligence.lifecycle.strategy_lifecycle_manager import (
    StrategyLifecycleManager
)

from intelligence.lifecycle.lifecycle_history import LifecycleHistory





class IntelligenceComponents:

    def __init__(self):

        # Decision Intelligence

        self.reasoning = ReasoningEngine()

        self.regime_analyzer = RegimeAnalyzer()

        self.risk_analyzer = RiskAnalyzer()

        self.decision_engine = DecisionEngine()

        self.decision_validator = DecisionValidator()

        self.decision_memory = DecisionMemory()

        self.decision_quality = DecisionQualityAnalyzer()

        # Strategy Intelligence

        self.strategy_memory = StrategyMemory()

        self.strategy_history = StrategyHistory()

        self.strategy_performance = StrategyPerformanceAnalyzer()


        self.strategy_learner = StrategyLearner(
            self.strategy_memory
        )


        self.strategy_recall = StrategyRecall(
            self.strategy_memory
        )


        self.strategy_ranker = StrategyRanker()


        self.strategy_selector = StrategySelector(
            self.strategy_recall,
            self.strategy_ranker
        )


        self.strategy_intelligence_adapter = (
            StrategyIntelligenceAdapter()
        )


        self.strategy_intelligence = (
            StrategyIntelligenceService()
        )


        self.strategy_context = StrategyContext(
            self.strategy_recall
        )


        self.strategy_feedback = StrategyFeedback()


        self.strategy_quality_gate = StrategyQualityGate()


        self.strategy_improvement = (
            StrategyImprovementEngine()
        )


        self.strategy_bridge = StrategyBridge()


        self.strategy_update = StrategyUpdate(
            self.strategy_memory,
            self.strategy_quality_gate,
            self.strategy_history
        )

        # Governance Intelligence

        self.strategy_governance = StrategyGovernance()


        self.governance_memory = GovernanceMemory()


        self.governance_feedback = GovernanceFeedback(
            self.governance_memory
        )

        self.governance_confidence = GovernanceConfidence()

        # Evolution Intelligence

        self.evolution_history = EvolutionHistory()


        self.evolution_recall = EvolutionRecall(
            self.evolution_history
        )


        self.evolution_recall_analyzer = EvolutionRecallAnalyzer(
            self.evolution_recall
        )


        self.evolution_intelligence = EvolutionIntelligence(
            self.evolution_recall_analyzer
        )


        self.self_evolution_controller = SelfEvolutionController(

            evolution_engine=StrategyEvolutionEngine(
                history=self.evolution_history
            ),

            analytics=EvolutionAnalytics(
                self.evolution_history
            ),

            decision=EvolutionDecision(),

            rollback=RollbackEngine(
                self.evolution_history
            ),

            history=self.evolution_history,

            recall=self.evolution_recall,

            intelligence=self.evolution_intelligence
        )


        self.evolution_execution = EvolutionExecution(
            self.self_evolution_controller
        )


        # Strategy Lifecycle Intelligence

        self.lifecycle_history = LifecycleHistory()

        self.strategy_lifecycle = StrategyLifecycleManager(
            self.lifecycle_history
        )