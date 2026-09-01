from intelligence.reasoning import ReasoningEngine
from intelligence.regime_analyzer import RegimeAnalyzer
from intelligence.risk_analyzer import RiskAnalyzer

from intelligence.decision_engine import DecisionEngine
from intelligence.decision_validator import DecisionValidator
from intelligence.decision_memory import DecisionMemory
from intelligence.decision_quality import DecisionQualityAnalyzer

from intelligence.decision_outcome_bridge import (
    DecisionOutcomeBridge
)


# ============================================================
# Core Memory
# ============================================================

from intelligence.memory.experience_memory import (
    ExperienceMemory
)

from intelligence.memory.outcome_memory import (
    OutcomeMemory
)

from intelligence.meta.meta_memory import MetaMemory

from intelligence.memory.strategy_performance_memory import (
    StrategyPerformanceMemory
)


# ============================================================
# Performance & Feedback Intelligence
# ============================================================

from intelligence.performance_feedback import (
    PerformanceFeedback
)

from intelligence.performance_learning_adapter import (
    PerformanceLearningAdapter
)


# ============================================================
# Adaptive & Learning Intelligence
# ============================================================

from intelligence.pattern_service import (
    PatternService
)

from intelligence.pattern_intelligence import (
    PatternIntelligence
)

from intelligence.scenario_engine import (
    ScenarioEngine
)

from intelligence.learning_analyzer import (
    LearningAnalyzer
)

from intelligence.learning.strategy_evolution_decision import (
    StrategyEvolutionDecision
)

from intelligence.adaptive_confidence import (
    AdaptiveConfidence
)

from intelligence.experience_confidence import (
    ExperienceConfidence
)

from intelligence.confidence_adjuster import (
    ConfidenceAdjuster
)

from intelligence.adaptive_intelligence import (
    AdaptiveIntelligence
)

from intelligence.meta.meta_learning_engine import (
    MetaLearningEngine
)


# ============================================================
# Strategy Intelligence
# ============================================================

from intelligence.strategy_analyzer import (
    StrategyAnalyzer
)

from intelligence.strategy_council import (
    StrategyCouncil
)

from intelligence.strategy_memory import (
    StrategyMemory
)

from intelligence.learning.strategy_history import (
    StrategyHistory
)

from intelligence.learning.strategy_evolution_decision import (
    StrategyEvolutionDecision
)

from intelligence.learning.strategy_performance import (
    StrategyPerformanceAnalyzer
)

from intelligence.strategy_learner import (
    StrategyLearner
)

from intelligence.strategy_recall import (
    StrategyRecall
)

from intelligence.learning.strategy_ranker import (
    StrategyRanker
)

from intelligence.strategy_selector import (
    StrategySelector
)

from intelligence.strategy_intelligence_adapter import (
    StrategyIntelligenceAdapter
)

from intelligence.strategy_intelligence_service import (
    StrategyIntelligenceService
)

from intelligence.strategy_context import (
    StrategyContext
)

from intelligence.strategy_feedback import (
    StrategyFeedback
)

from intelligence.learning.strategy_quality_gate import (
    StrategyQualityGate
)

from intelligence.learning.strategy_improvement_engine import (
    StrategyImprovementEngine
)

from intelligence.learning.strategy_update import (
    StrategyUpdate
)

from intelligence.strategy_bridge import (
    StrategyBridge
)

from intelligence.strategy_governance import (
    StrategyGovernance
)


# ============================================================
# Governance Intelligence
# ============================================================

from intelligence.governance.governance_memory import (
    GovernanceMemory
)

from intelligence.governance.governance_feedback import (
    GovernanceFeedback
)

from intelligence.governance.governance_confidence import (
    GovernanceConfidence
)


# ============================================================
# Evolution Intelligence
# ============================================================

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

from intelligence.evolution.evolution_execution import (
    EvolutionExecution
)

from intelligence.evolution.evolution_analytics import (
    EvolutionAnalytics
)

from intelligence.evolution.evolution_decision import (
    EvolutionDecision
)

from intelligence.evolution.self_evolution_controller import (
    SelfEvolutionController
)

from intelligence.evolution.rollback_engine import (
    RollbackEngine
)

from intelligence.learning.strategy_evolution_engine import (
    StrategyEvolutionEngine
)


# ============================================================
# Lifecycle Intelligence
# ============================================================

from intelligence.lifecycle.lifecycle_analytics import (
    LifecycleAnalytics
)

from intelligence.lifecycle.lifecycle_history import (
    LifecycleHistory
)

from intelligence.lifecycle.strategy_lifecycle_manager import (
    StrategyLifecycleManager
)


# ============================================================
# Meta Intelligence
# ============================================================

from intelligence.meta.meta_intelligence import (
    MetaIntelligence
)


class IntelligenceComponents:

    """
    Phoenix Genesis Intelligence Composition Root.

    This class owns dependency construction and explicitly
    wires shared dependencies between intelligence components.

    Components should not be responsible for constructing
    their own collaborators when those collaborators are
    supplied by this composition root.
    """

    def __init__(self):

        # ====================================================
        # Decision Intelligence
        # ====================================================

        self.reasoning = ReasoningEngine()

        self.regime_analyzer = RegimeAnalyzer()

        self.risk_analyzer = RiskAnalyzer()

        self.decision_engine = DecisionEngine()

        self.decision_validator = DecisionValidator()

        self.decision_memory = DecisionMemory()

        self.decision_quality = DecisionQualityAnalyzer()


        # ====================================================
        # Shared Memory
        # ====================================================

        self.experience_memory = ExperienceMemory()

        self.outcome_memory = OutcomeMemory()

        self.meta_memory = MetaMemory()

        self.strategy_performance_memory = (
            StrategyPerformanceMemory()
        )


        # ====================================================
        # Performance & Outcome Learning
        # ====================================================

        self.performance_feedback = (
            PerformanceFeedback()
        )

        self.performance_learning = (
            PerformanceLearningAdapter(
                self.experience_memory
            )
        )

        self.decision_outcome_bridge = (
            DecisionOutcomeBridge(

                outcome_memory=self.outcome_memory,

                performance_feedback=(
                    self.performance_feedback
                ),

                strategy_performance_memory=(
                    self.strategy_performance_memory
                ),

                performance_learning=(
                    self.performance_learning
                )
            )
        )


        # ====================================================
        # Core Learning Intelligence
        # ====================================================

        self.pattern_service = PatternService()

        self.pattern_intelligence = PatternIntelligence()

        self.scenario_engine = ScenarioEngine()

        self.learning_analyzer = LearningAnalyzer()

        self.adaptive_confidence = AdaptiveConfidence()

        self.experience_confidence = (
            ExperienceConfidence()
        )

        self.confidence_adjuster = (
            ConfidenceAdjuster()
        )

        self.adaptive_intelligence = (
            AdaptiveIntelligence(

                adaptive_confidence=(
                    self.adaptive_confidence
                ),

                experience_confidence=(
                    self.experience_confidence
                ),

                confidence_adjuster=(
                    self.confidence_adjuster
                )
            )
        )


        # ====================================================
        # Strategy Intelligence
        # ====================================================

        self.strategy_analyzer = StrategyAnalyzer()

        self.strategy_council = StrategyCouncil()

        self.strategy_memory = StrategyMemory()

        self.meta_intelligence = MetaIntelligence()

        self.meta_learning_engine = (
            MetaLearningEngine()
        )

        self.strategy_history = StrategyHistory()

        self.strategy_performance = (
            StrategyPerformanceAnalyzer()
        )


        # ----------------------------------------------------
        # Strategy Learning
        # ----------------------------------------------------

        self.strategy_learner = (
            StrategyLearner(
                self.strategy_memory
            )
        )


        # ----------------------------------------------------
        # Strategy Recall
        # ----------------------------------------------------

        self.strategy_recall = (
            StrategyRecall(
                self.strategy_memory
            )
        )


        # ----------------------------------------------------
        # Strategy Ranking & Selection
        # ----------------------------------------------------

        self.strategy_ranker = StrategyRanker()

        self.strategy_selector = (
            StrategySelector(
                self.strategy_recall,
                self.strategy_ranker
            )
        )


        # ----------------------------------------------------
        # Strategy Intelligence Services
        # ----------------------------------------------------

        self.strategy_intelligence_adapter = (
            StrategyIntelligenceAdapter()
        )

        self.strategy_intelligence = (
            StrategyIntelligenceService()
        )

        self.strategy_context = (
            StrategyContext(
                self.strategy_recall
            )
        )

        self.strategy_feedback = StrategyFeedback()


        # ----------------------------------------------------
        # Strategy Quality & Improvement
        # ----------------------------------------------------

        self.strategy_quality_gate = (
            StrategyQualityGate()
        )

        self.strategy_improvement = (
            StrategyImprovementEngine()
        )

        self.strategy_update = (
            StrategyUpdate(

                self.strategy_memory,

                self.strategy_quality_gate,

                self.strategy_history
            )
        )


        # ----------------------------------------------------
        # Strategy Governance & Bridge
        # ----------------------------------------------------

        self.strategy_governance = StrategyGovernance()

        self.strategy_bridge = StrategyBridge()


        # ====================================================
        # Governance Intelligence
        # ====================================================

        # Shared governance memory.
        #
        # All governance components that require this memory
        # should receive this same instance.

        self.governance_memory = GovernanceMemory()

        self.governance_feedback = (
            GovernanceFeedback(
                self.governance_memory
            )
        )

        self.governance_confidence = (
            GovernanceConfidence()
        )


        # ====================================================
        # Evolution Intelligence
        # ====================================================

        # Shared evolution history.
        #
        # Evolution components intentionally operate on the
        # same history instance.

        self.evolution_history = EvolutionHistory()

        self.evolution_recall = (
            EvolutionRecall(
                self.evolution_history
            )
        )

        self.evolution_recall_analyzer = (
            EvolutionRecallAnalyzer(
                self.evolution_recall
            )
        )

        self.evolution_intelligence = (
            EvolutionIntelligence(
                self.evolution_recall_analyzer
            )
        )


        # ----------------------------------------------------
        # Evolution Engine
        # ----------------------------------------------------

        self.strategy_evolution_engine = (
            StrategyEvolutionEngine(
                history=self.evolution_history
            )
        )

        self.strategy_evolution_decision = (
            StrategyEvolutionDecision(
                self.strategy_evolution_engine
            )
        )


        # ----------------------------------------------------
        # Evolution Analytics
        # ----------------------------------------------------

        self.evolution_analytics = (
            EvolutionAnalytics(
                self.evolution_history
            )
        )


        # ----------------------------------------------------
        # Evolution Decision
        # ----------------------------------------------------

        self.evolution_decision = EvolutionDecision()


        # ----------------------------------------------------
        # Rollback
        # ----------------------------------------------------

        self.rollback_engine = (
            RollbackEngine(
                self.evolution_history
            )
        )


        # ----------------------------------------------------
        # Self Evolution Controller
        # ----------------------------------------------------

        self.self_evolution_controller = (
            SelfEvolutionController(

                evolution_engine=(
                    self.strategy_evolution_engine
                ),

                analytics=(
                    self.evolution_analytics
                ),

                decision=(
                    self.evolution_decision
                ),

                rollback=(
                    self.rollback_engine
                ),

                history=(
                    self.evolution_history
                ),

                recall=(
                    self.evolution_recall
                ),

                intelligence=(
                    self.evolution_intelligence
                )
            )
        )


        # ----------------------------------------------------
        # Evolution Execution
        # ----------------------------------------------------

        self.evolution_execution = (
            EvolutionExecution(
                self.self_evolution_controller
            )
        )


        # ====================================================
        # Strategy Lifecycle Intelligence
        # ====================================================

        self.lifecycle_history = LifecycleHistory()

        self.lifecycle_analytics = LifecycleAnalytics()

        self.strategy_lifecycle = (
            StrategyLifecycleManager(
                self.lifecycle_history
            )
        )