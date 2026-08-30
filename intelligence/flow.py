from intelligence.action_proposal import ActionProposal
from intelligence.decision_memory import DecisionMemory
from intelligence.decision_outcome_bridge import DecisionOutcomeBridge
from intelligence.decision_record import DecisionRecord
from intelligence.decision_validator import DecisionValidator
from intelligence.decision_engine import DecisionEngine
from intelligence.decision_quality import DecisionQualityAnalyzer

from intelligence.experience_confidence import ExperienceConfidence
from intelligence.experience_context import ExperienceContext
from intelligence.intelligence_context import IntelligenceContext

from intelligence.historical_context import HistoricalContext
from intelligence.learning_analyzer import LearningAnalyzer
from intelligence.adaptive_learning_context import (
    AdaptiveLearningContextBuilder
)

from intelligence.adaptive_confidence import AdaptiveConfidence
from intelligence.adaptive_intelligence import AdaptiveIntelligence
from intelligence.confidence_adjuster import ConfidenceAdjuster

from intelligence.memory.experience_memory import ExperienceMemory
from intelligence.memory.outcome_memory import OutcomeMemory
from intelligence.memory.strategy_performance_memory import (
    StrategyPerformanceMemory
)

from intelligence.meta.meta_confidence_adapter import (
    MetaConfidenceAdapter
)
from intelligence.meta.meta_feedback import MetaFeedbackRecord
from intelligence.meta.meta_intelligence import MetaIntelligence
from intelligence.meta.meta_learning_engine import MetaLearningEngine
from intelligence.meta.meta_memory import MetaMemory

from intelligence.pattern_intelligence import PatternIntelligence
from intelligence.pattern_service import PatternService

from intelligence.performance_feedback import PerformanceFeedback
from intelligence.performance_learning_adapter import (
    PerformanceLearningAdapter
)

from intelligence.regime_analyzer import RegimeAnalyzer
from intelligence.reasoning import ReasoningEngine
from intelligence.risk_analyzer import RiskAnalyzer
from intelligence.report import MarketReport
from intelligence.scenario_engine import ScenarioEngine

from intelligence.strategy_analyzer import StrategyAnalyzer
from intelligence.strategy_bridge import StrategyBridge
from intelligence.strategy_consensus_validator import (
    StrategyConsensusValidator
)
from intelligence.strategy_context import StrategyContext
from intelligence.strategy_council import StrategyCouncil
from intelligence.strategy_governance import StrategyGovernance
from intelligence.strategy_intelligence_adapter import (
    StrategyIntelligenceAdapter
)
from intelligence.strategy_intelligence_service import (
    StrategyIntelligenceService
)
from intelligence.strategy_learner import StrategyLearner
from intelligence.strategy_memory import StrategyMemory
from intelligence.strategy_recall import StrategyRecall
from intelligence.strategy_selector import StrategySelector

from intelligence.learning.strategy_evolution_flow import (
    StrategyEvolutionFlow
)
from intelligence.learning.strategy_history import StrategyHistory
from intelligence.learning.strategy_ranker import StrategyRanker

from intelligence.governance.governance_record import GovernanceRecord

from intelligence.lifecycle.lifecycle_analytics import (
    LifecycleAnalytics
)

from intelligence.evolution.evolution_analytics import (
    EvolutionAnalytics
)
from intelligence.evolution.evolution_explainer import (
    EvolutionExplainer
)

from intelligence.evolution.evolution_intelligence import (
    EvolutionIntelligence
)

from intelligence.evolution.evolution_ranker import EvolutionRanker

from intelligence.evolution.evolution_report_builder import (
    EvolutionReportBuilder
)

from intelligence.components.intelligence_components import (
    IntelligenceComponents
)


class IntelligenceFlow:

    def __init__(self):

        # ---------------------------------------------------------
        # Core intelligence
        # ---------------------------------------------------------

        self.components = IntelligenceComponents()

        self.pattern_service = (
            self.components.pattern_service
        )
        self.pattern_intelligence = (
            self.components.pattern_intelligence
        )

        self.scenario_engine = (
            self.components.scenario_engine
        )

        self.learning_analyzer = (
            self.components.learning_analyzer
        )

        self.adaptive_confidence = (
            self.components.adaptive_confidence
        )
        self.experience_confidence = (
            self.components.experience_confidence
        )
        self.confidence_adjuster = (
            self.components.confidence_adjuster
        )

        self.adaptive_intelligence = (
            self.components.adaptive_intelligence
        )

        self.adaptive_learning_context_builder = (
            AdaptiveLearningContextBuilder()
        )

        # ---------------------------------------------------------
        # Memory
        # ---------------------------------------------------------

        self.experience_memory = (
            self.components.experience_memory
        )

        self.experience_context = ExperienceContext(
            self.experience_memory
        )

        self.strategy_memory = (
            self.components.strategy_memory
        )

        self.strategy_history = (
            self.components.strategy_history
        )

        self.strategy_performance_memory = (
            self.components.strategy_performance_memory
        )

        self.outcome_memory = (
            self.components.outcome_memory
        )

        self.meta_memory = (
            self.components.meta_memory
        )

        # ---------------------------------------------------------
        # Strategy intelligence
        # ---------------------------------------------------------

        
        self.strategy_analyzer = (
            self.components.strategy_analyzer
        )

        self.strategy_performance = (
            self.components.strategy_performance
        )

        self.strategy_learner = (
            self.components.strategy_learner
        )

        self.strategy_recall = (
            self.components.strategy_recall
        )

        self.strategy_ranker = (
            self.components.strategy_ranker
        )

        self.strategy_council = (
            self.components.strategy_council
        )

        self.strategy_consensus_validator = (
            StrategyConsensusValidator()
        )

        self.strategy_selector = (
            self.components.strategy_selector
        )

        self.strategy_bridge = (
            self.components.strategy_bridge
        )

        self.strategy_context = (
            self.components.strategy_context
        )

        self.strategy_intelligence_adapter = (
            self.components.strategy_intelligence_adapter
        )

        self.strategy_intelligence = (
            self.components.strategy_intelligence
        )

        self.strategy_feedback = (
            self.components.strategy_feedback
        )

        self.strategy_quality_gate = (
            self.components.strategy_quality_gate
        )

        self.strategy_improvement = (
            self.components.strategy_improvement
        )

        self.strategy_update = (
            self.components.strategy_update
        )

        # ---------------------------------------------------------
        # Strategy learning / evolution
        # ---------------------------------------------------------
           

        self.strategy_evolution_flow = (
            StrategyEvolutionFlow(
                performance_analyzer=self.strategy_performance,
                governance_memory=self.components.governance_memory
            )
        )

        
        # ---------------------------------------------------------
        # Performance / outcome learning
        # ---------------------------------------------------------

        self.performance_feedback = (
            self.components.performance_feedback
        )

        self.performance_learning = (
            self.components.performance_learning
        )

        self.decision_outcome_bridge = (
            self.components.decision_outcome_bridge
        )

        # ---------------------------------------------------------
        # Decision layer
        # ---------------------------------------------------------

        self.reasoning = self.components.reasoning
        self.regime_analyzer = self.components.regime_analyzer
        self.risk_analyzer = self.components.risk_analyzer

        self.decision_engine = self.components.decision_engine
        self.decision_validator = (
            self.components.decision_validator
        )
        self.decision_memory = self.components.decision_memory
        self.decision_quality = self.components.decision_quality

        # ---------------------------------------------------------
        # Governance
        # ---------------------------------------------------------

        self.strategy_governance = (
            self.components.strategy_governance
        )

        self.governance_memory = (
            self.components.governance_memory
        )

        self.governance_feedback = (
            self.components.governance_feedback
        )

        self.governance_confidence = (
            self.components.governance_confidence
        )

        # ---------------------------------------------------------
        # Evolution
        # ---------------------------------------------------------

        self.evolution_history = (
            self.components.evolution_history
        )

        self.evolution_recall = (
            self.components.evolution_recall
        )

        self.evolution_recall_analyzer = (
            self.components.evolution_recall_analyzer
        )

        self.evolution_intelligence = (
            self.components.evolution_intelligence
        )

        self.self_evolution_controller = (
            self.components.self_evolution_controller
        )

        self.evolution_execution = (
            self.components.evolution_execution
        )

        # ---------------------------------------------------------
        # Lifecycle
        # ---------------------------------------------------------

        self.strategy_lifecycle = (
            self.components.strategy_lifecycle
        )

        self.lifecycle_analytics = (
            self.components.lifecycle_analytics
        )

        # ---------------------------------------------------------
        # Meta intelligence
        # ---------------------------------------------------------

        self.meta_intelligence = (
            self.components.meta_intelligence
        )

        self.meta_confidence_adapter = (
            MetaConfidenceAdapter()
        )

        self.meta_learning_engine = (
            MetaLearningEngine()
        )


    # =============================================================
    # REPORT CREATION
    # =============================================================

    def create_report(self, consensus):

        # ---------------------------------------------------------
        # 1. Historical learning
        # ---------------------------------------------------------

        learning_insight = (
            self.learning_analyzer.analyze(
                self.decision_memory.records
            )
        )

        # Do not hardcode "Trend".
        # At this stage there is no selected strategy yet.
        experience_context = (
            self.experience_context.build_context(
                strategy=None
            )
        )

        # ---------------------------------------------------------
        # 2. Market analysis
        # ---------------------------------------------------------

        if consensus is None:

            regime = type(
                "RegimeResult",
                (),
                {
                    "regime": "UNKNOWN",
                    "reasons": []
                }
            )()

            risk = type(
                "RiskResult",
                (),
                {
                    "level": "UNKNOWN",
                    "reason": "No market consensus available",
                    "reasons": []
                }
            )()

            analysis = {
                "summary": "No market analysis available",
                "confidence": 0,
                "signal": "WAIT",
                "reasons": []
            }

        else:

            regime = self.regime_analyzer.analyze(
                consensus
            )

            risk = self.risk_analyzer.analyze(
                consensus
            )

            analysis = self.reasoning.generate(
                consensus,
                risk
            )

        # ---------------------------------------------------------
        # 3. Adaptive confidence
        # ---------------------------------------------------------

        adaptive_learning_context = (
            self.adaptive_learning_context_builder.build(

                base_confidence=(
                    analysis["confidence"]
                ),

                learning_insight=learning_insight,

                experience_context=experience_context
            )
        )

        analysis["confidence"] = (
            self.adaptive_intelligence
            .adjust_context_confidence(
                adaptive_learning_context
            )
        )

        # ---------------------------------------------------------
        # 4. Scenario intelligence
        # ---------------------------------------------------------

        scenarios = self.scenario_engine.generate(

            regime.regime,

            analysis["confidence"],

            risk.level
        )

        if consensus is None:

            trend = "UNKNOWN"
            signal = "WAIT"

        else:

            trend = consensus.trend
            signal = analysis["signal"]

        # ---------------------------------------------------------
        # 5. Market report
        # ---------------------------------------------------------

        report = MarketReport(

            symbol="BTCUSDT",

            timeframe="Multi",

            trend=trend,

            regime=regime.regime,

            signal=signal,

            confidence=analysis["confidence"],

            risk=risk.level,

            reasons=[

                f"Market Regime: {regime.regime}",

                f"Risk Level: {risk.level}",

                (
                    "Historical Reliability: "
                    f"{learning_insight.reliability}"
                ),

                *regime.reasons,

                *risk.reasons,

                *analysis["reasons"]
            ]
        )

        report.scenarios = scenarios
        report.learning_insight = learning_insight
        report.experience_context = experience_context

        # ---------------------------------------------------------
        # 6. Strategy selection
        # ---------------------------------------------------------

        strategy_selection = (
            self.strategy_selector.select_with_result(

                report.regime,

                report.signal,

                report.risk
            )
        )

        best_strategy = None
        champion_strategy = None

        if strategy_selection:

            best_strategy = (
                strategy_selection["champion"]
            )

            report.strategy_ranking = (
                strategy_selection["ranking"]
            )

            report.strategy_consensus = (
                self.strategy_council.evaluate(
                    strategy_selection["ranking"]
                )
            )

            report.strategy_consensus_gate = (
                self.strategy_consensus_validator.explain(
                    report.strategy_consensus
                )
            )

        # ---------------------------------------------------------
        # 7. Champion strategy
        # ---------------------------------------------------------

        if best_strategy:

            champion_strategy = (
                self.strategy_bridge.get_best_strategy(
                    [best_strategy]
                )
            )

        report.champion_strategy = champion_strategy

        # ---------------------------------------------------------
        # 8. Strategy intelligence
        # ---------------------------------------------------------

        report.strategy_intelligence = None

        strategy_history = []

        strategy_intelligence_context = None
        strategy_knowledge = None

        if best_strategy:

            strategy_history = (
                self.strategy_history.get_history(
                    best_strategy["name"]
                )
            )

            (
                strategy_intelligence_context,
                strategy_knowledge
            ) = (
                self.strategy_intelligence_adapter
                .build_context(
                    best_strategy,
                    strategy_history
                )
            )

        if strategy_intelligence_context:

            report.strategy_intelligence = (
                self.strategy_intelligence.analyze(
                    strategy_intelligence_context,
                    strategy_knowledge
                )
            )

        # ---------------------------------------------------------
        # 9. Strategy evolution evaluation
        # ---------------------------------------------------------

        if strategy_history:

            evolution_result = (
                self.strategy_evolution_flow.evaluate(
                    best_strategy,
                    strategy_history
                )
            )

        else:

            evolution_result = {
                "strategy": best_strategy,
                "evolution": {
                    "action": "NEW",
                    "reason": "no history"
                }
            }

        report.strategy_evolution = evolution_result

        # ---------------------------------------------------------
        # 10. Self evolution governance
        # ---------------------------------------------------------

        self_evolution_result = None

        if best_strategy:

            score = best_strategy.get(
                "score",
                0
            )

            evolution_permission = (
                self.evolution_intelligence.evaluate(
                    best_strategy["name"]
                )
            )

            if (
                evolution_permission["decision"]
                == "ALLOW"
            ):

                self_evolution_result = (
                    self.self_evolution_controller.run(
                        best_strategy,
                        score
                    )
                )

            else:

                self_evolution_result = {

                    "action": "BLOCKED",

                    "reason": (
                        evolution_permission["decision"]
                    ),

                    "intelligence": evolution_permission
                }

        report.self_evolution_result = (
            self_evolution_result
        )

        report.evolution_execution = None

        # ---------------------------------------------------------
        # 11. Strategy context + strategy confidence
        # ---------------------------------------------------------

        if best_strategy:

            report.strategy_context = (
                self.strategy_context.analyze(

                    report.regime,

                    report.signal,

                    report.risk
                )
            )

            report.confidence = (
                self.adaptive_intelligence
                .adjust_strategy_confidence(

                    report.confidence,

                    best_strategy
                )
            )

        else:

            report.strategy_context = None

        # ---------------------------------------------------------
        # 12. Strategy governance
        # ---------------------------------------------------------

        if best_strategy:

            governance_result = (
                self.strategy_governance.evaluate(
                    best_strategy
                )
            )

            governance_record = GovernanceRecord(

                strategy=best_strategy,

                status=governance_result["status"],

                reason=governance_result["reason"]
            )

            self.governance_memory.store(
                governance_record
            )

            report.governance_result = (
                governance_result
            )

        # ---------------------------------------------------------
        # 13. Decision
        # ---------------------------------------------------------

        decision = self.decision_engine.decide(
            report
        )

        report.decision = decision

        report.strategy_insight = (
            self.strategy_analyzer.analyze(
                decision,
                report
            )
        )

        # ---------------------------------------------------------
        # 14. Resolve strategy identity for outcome learning
        # ---------------------------------------------------------

        performance_strategy = None

        if champion_strategy:

            performance_strategy = (
                champion_strategy.get("name")
            )

        if performance_strategy is None:

            performance_strategy = (
                f"{report.regime}_"
                f"{report.signal}_"
                f"{report.risk}"
            )

        # ---------------------------------------------------------
        # 15. Decision -> Outcome -> Performance
        # ---------------------------------------------------------

        outcome_result = (
            self.decision_outcome_bridge.process(

                decision=decision,

                entry_price=65000,

                exit_price=67000,

                strategy=performance_strategy
            )
        )

        report.performance_feedback = (
            outcome_result["feedback"]
        )

        report.performance_learning = (
            outcome_result.get(
                "performance_learning"
            )
        )

        strategy_record = (
            outcome_result.get(
                "performance"
            )
        )

        # ---------------------------------------------------------
        # 16. Strategy performance analysis
        # ---------------------------------------------------------

        strategy_name = (
            report.strategy_insight["strategy"]
        )

        strategy_history = (
            self.strategy_history.get_history(
                strategy_name
            )
        )

        strategy_performance = (
            self.strategy_performance.analyze(
                strategy_history
            )
        )

        # ---------------------------------------------------------
        # 17. Strategy improvement
        # ---------------------------------------------------------

        if strategy_record:

            improved_strategy = (
                self.strategy_improvement.improve(

                    strategy_record.strategy,

                    report.strategy_insight["score"],

                    [strategy_record]
                )
            )

            self.strategy_update.update(
                improved_strategy
            )

        # Refresh after possible strategy update.
        strategy_history = (
            self.strategy_history.get_history(
                strategy_name
            )
        )

        strategy_performance = (
            self.strategy_performance.analyze(
                strategy_history
            )
        )

        # ---------------------------------------------------------
        # 18. Experience -> Pattern Intelligence
        # ---------------------------------------------------------

        patterns = (
            self.pattern_intelligence.analyze(
                self.experience_memory.get_experiences()
            )
        )

        report.pattern_insight = patterns

        # ---------------------------------------------------------
        # 19. Pattern -> Strategy Learning
        # ---------------------------------------------------------

        if patterns:

            learned_strategies = (
                self.strategy_learner.learn(
                    patterns
                )
            )

            report.learned_strategies = (
                learned_strategies
            )

        else:

            report.learned_strategies = []

        # ---------------------------------------------------------
        # 20. Historical context
        # ---------------------------------------------------------

        historical_context = HistoricalContext(

            pattern=(
                f"{report.regime} + "
                f"{decision.action}"
            ),

            confidence=(
                learning_insight.average_confidence
            ),

            samples=learning_insight.samples,

            reliability=learning_insight.reliability
        )

        report.historical_context = (
            historical_context
        )

        # ---------------------------------------------------------
        # 21. Decision validation
        # ---------------------------------------------------------

        is_valid = (
            self.decision_validator.validate(
                decision
            )
        )

        if is_valid:

            report.action_proposal = ActionProposal(

                action=decision.action,

                status="APPROVED",

                reason=decision.reason,

                confidence=decision.confidence
            )

        else:

            report.action_proposal = ActionProposal(

                action=decision.action,

                status="REJECTED",

                reason=decision.reason,

                confidence=decision.confidence
            )

        # ---------------------------------------------------------
        # 22. Decision record
        # ---------------------------------------------------------

        record = DecisionRecord(

            symbol=report.symbol,

            timeframe=report.timeframe,

            regime=report.regime,

            signal=report.signal,

            confidence=report.confidence,

            risk=report.risk,

            action=decision.action,

            validation_status=(
                report.action_proposal.status
            ),

            trace=(
                decision.metadata.get("trace")
                if hasattr(decision, "metadata")
                else None
            ),

            strategy=getattr(
                report,
                "champion_strategy",
                None
            )
        )

        # ---------------------------------------------------------
        # 23. Decision quality
        # ---------------------------------------------------------

        quality_result = (
            self.decision_quality.calculate(
                record
            )
        )

        record.quality_score = (
            quality_result["quality_score"]
        )

        self.decision_memory.store(
            record
        )

        # ---------------------------------------------------------
        # 24. Meta intelligence
        # ---------------------------------------------------------

        report.meta_insight = (
            self.meta_intelligence.analyze(

                self.decision_memory.records,

                self.meta_memory.get_records()
            )
        )

        report.meta_learning = (
            self.meta_learning_engine.learn(
                report.meta_insight
            )
        )

        confidence_before = report.confidence

        report.confidence = (
            self.meta_confidence_adapter.adjust(

                report.confidence,

                report.meta_learning
            )
        )

        adjustment = (
            report.confidence
            - confidence_before
        )

        meta_feedback = MetaFeedbackRecord(

            confidence_before=confidence_before,

            adjustment=adjustment,

            confidence_after=report.confidence,

            outcome=(
                outcome_result["result"]
            ),

            meta_effective=(
                outcome_result["result"]
                == "SUCCESS"
            )
        )

        self.meta_memory.store(
            meta_feedback
        )

        report.meta_feedback = meta_feedback

        # Refresh meta insight after feedback.
        report.meta_insight = (
            self.meta_intelligence.analyze(

                self.decision_memory.records,

                self.meta_memory.get_records()
            )
        )

        # ---------------------------------------------------------
        # 25. Unified Intelligence Context
        # ---------------------------------------------------------

        report.intelligence_context = IntelligenceContext(

            historical_context=historical_context,

            learning_insight=getattr(
                report,
                "learning_insight",
                None
            ),

            pattern_insight=getattr(
                report,
                "pattern_insight",
                None
            ),

            quality_score=getattr(
                record,
                "quality_score",
                0
            ),

            adaptive_confidence=report.confidence
        )

        # ---------------------------------------------------------
        # 26. Refresh strategy context
        # ---------------------------------------------------------

        report.strategy_context = (
            self.strategy_context.analyze(

                report.regime,

                report.signal,

                report.risk
            )
        )

        report.strategy_performance = (
            strategy_performance
        )

        # ---------------------------------------------------------
        # 27. Lifecycle intelligence
        # ---------------------------------------------------------

        report.strategy_lifecycle = None

        if best_strategy:

            report.strategy_lifecycle = (
                self.lifecycle_analytics.analyze(

                    best_strategy["name"],

                    self.strategy_lifecycle.history
                )
            )

        # ---------------------------------------------------------
        # 28. Self-evolution status
        # ---------------------------------------------------------

        report.self_evolution = {

            "status": "READY",

            "controller": (
                self.self_evolution_controller
                is not None
            )
        }

        # ---------------------------------------------------------
        # 29. Final evolution report
        # ---------------------------------------------------------

        if hasattr(
            self,
            "evolution_history"
        ):

            evolution_builder = (
                EvolutionReportBuilder(

                    EvolutionAnalytics(
                        self.evolution_history
                    ),

                    EvolutionRanker(),

                    EvolutionExplainer()
                )
            )

            evolution_report = (
                evolution_builder.build()
            )

            if (
                "summary" in evolution_report
                and
                evolution_report["summary"].get(
                    "best_strategy"
                ) is None
            ):

                history = (
                    getattr(
                        self.evolution_history,
                        "_records",
                        []
                    )
                )

                if history:

                    evolution_report[
                        "summary"
                    ]["best_strategy"] = (
                        history[-1].child
                    )

            report.evolution = evolution_report

        else:

            report.evolution = {

                "summary": {

                    "total_evolutions": 0,

                    "best_strategy": None
                },

                "history": []
            }

        return report


    # =============================================================
    # BUILD REPORT
    # =============================================================

    def build_report(self):

        report = {}

        if hasattr(
            self,
            "evolution_history"
        ):

            builder = EvolutionReportBuilder(

                EvolutionAnalytics(
                    self.evolution_history
                ),

                EvolutionRanker(),

                EvolutionExplainer()
            )

            report["evolution"] = (
                builder.build()
            )

        else:

            report["evolution"] = {

                "summary": {

                    "total_evolutions": 0,

                    "best_strategy": None
                }
            }

        return report


    # =============================================================
    # GOVERNANCE FEEDBACK
    # =============================================================

    def update_governance_feedback(
        self,
        strategy,
        outcome
    ):

        feedback = (
            self.governance_feedback.evaluate(
                strategy,
                outcome
            )
        )

        confidence = (
            self.governance_confidence.calculate(
                feedback
            )
        )

        return {

            "feedback": feedback,

            "confidence": confidence
        }
