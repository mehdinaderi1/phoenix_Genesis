from intelligence.decision_memory import DecisionMemory
from intelligence.decision_record import DecisionRecord
from intelligence.decision_validator import DecisionValidator
from intelligence.decision_engine import DecisionEngine
from intelligence.decision_quality import DecisionQualityAnalyzer
from intelligence.action_proposal import ActionProposal
from intelligence.reasoning import ReasoningEngine
from intelligence.regime_analyzer import RegimeAnalyzer
from intelligence.risk_analyzer import RiskAnalyzer
from intelligence.report import MarketReport
from intelligence.pattern_service import PatternService
from intelligence.historical_context import HistoricalContext
from intelligence.adaptive_confidence import AdaptiveConfidence
from intelligence.intelligence_context import IntelligenceContext
from intelligence.scenario_engine import ScenarioEngine
from intelligence.performance_feedback import PerformanceFeedback
from intelligence.outcome_record import OutcomeRecord
from intelligence.experience_record import ExperienceRecord
from intelligence.experience_context import ExperienceContext
from intelligence.memory.experience_memory import ExperienceMemory
from intelligence.memory.strategy_performance_memory import StrategyPerformanceMemory
from intelligence.experience_confidence import ExperienceConfidence
from intelligence.confidence_adjuster import ConfidenceAdjuster
from intelligence.pattern_intelligence import PatternIntelligence

from intelligence.components.intelligence_components import (
    IntelligenceComponents
)


from intelligence.strategy_memory import StrategyMemory
from intelligence.strategy_analyzer import StrategyAnalyzer
from intelligence.strategy_recall import StrategyRecall
from intelligence.strategy_context import StrategyContext
from intelligence.strategy_feedback import StrategyFeedback
from intelligence.strategy_selector import StrategySelector
from intelligence.strategy_learner import StrategyLearner
from intelligence.strategy_intelligence_service import (
    StrategyIntelligenceService
)
from intelligence.strategy_intelligence_adapter import (
    StrategyIntelligenceAdapter
)
from intelligence.strategy_bridge import StrategyBridge
from intelligence.strategy_governance import StrategyGovernance



from intelligence.evolution.evolution_execution import (
    EvolutionExecution
)

from intelligence.evolution.self_evolution_controller import (
    SelfEvolutionController
)

from intelligence.learning.strategy_evolution_engine import (
    StrategyEvolutionEngine
)

from intelligence.evolution.evolution_history import (
    EvolutionHistory
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

from intelligence.evolution.evolution_intelligence import (
    EvolutionIntelligence
)

from intelligence.evolution.evolution_recall import (
    EvolutionRecall
)

from intelligence.evolution.evolution_recall_analyzer import (
    EvolutionRecallAnalyzer
)

from intelligence.evolution.evolution_report_builder import (
    EvolutionReportBuilder
)

from intelligence.evolution.evolution_analytics import (
    EvolutionAnalytics
)

from intelligence.evolution.evolution_ranker import (
    EvolutionRanker
)

from intelligence.evolution.evolution_explainer import (
    EvolutionExplainer
)




from intelligence.governance.governance_record import (
    GovernanceRecord
)
from intelligence.governance.governance_feedback import (
    GovernanceFeedback
)

from intelligence.governance.governance_confidence import (
    GovernanceConfidence
)




from intelligence.learning_analyzer import LearningAnalyzer
from intelligence.learning.strategy_ranker import StrategyRanker
from intelligence.learning.strategy_quality_gate import StrategyQualityGate
from intelligence.learning.strategy_evolution_flow import (
    StrategyEvolutionFlow
)
from intelligence.learning.strategy_history import StrategyHistory
from intelligence.learning.strategy_improvement_engine import StrategyImprovementEngine
from intelligence.learning.strategy_update import StrategyUpdate
from intelligence.learning.strategy_performance import (
    StrategyPerformanceAnalyzer
)

from intelligence.lifecycle.lifecycle_analytics import (
    LifecycleAnalytics
)


class IntelligenceFlow:

    def __init__(self):

       
        self.pattern_service = PatternService()

        self.pattern_intelligence = PatternIntelligence()

        self.components = IntelligenceComponents()
       
        self.scenario_engine = ScenarioEngine()

        self.learning_analyzer = LearningAnalyzer()

        self.adaptive_confidence = AdaptiveConfidence()

        self.experience_confidence = ExperienceConfidence()

        self.strategy_analyzer = StrategyAnalyzer()

        self.strategy_history = StrategyHistory()

        self.strategy_memory = StrategyMemory()

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

        
        self.strategy_intelligence = StrategyIntelligenceService()
        

        from intelligence.governance.governance_memory import (
            GovernanceMemory
        )
        

        self.strategy_context = StrategyContext(
            self.strategy_recall
        )

        self.confidence_adjuster = ConfidenceAdjuster()

        self.strategy_quality_gate = StrategyQualityGate()

        self.performance_feedback = PerformanceFeedback()

        self.strategy_feedback = StrategyFeedback()

        self.strategy_improvement = StrategyImprovementEngine()

        self.strategy_evolution_flow = StrategyEvolutionFlow(
            self.strategy_improvement
        )

        self.strategy_history = StrategyHistory()

        self.strategy_bridge = StrategyBridge()


        self.strategy_update = StrategyUpdate(
            self.strategy_memory,
            self.strategy_quality_gate,
            self.strategy_history
        )    

        self.experience_memory = ExperienceMemory()
        self.strategy_performance_memory = StrategyPerformanceMemory()
        self.experience_context = ExperienceContext(
            self.experience_memory
        )
       
        

        self.components = IntelligenceComponents()

        self.reasoning = self.components.reasoning
        self.regime_analyzer = self.components.regime_analyzer
        self.risk_analyzer = self.components.risk_analyzer
        self.decision_engine = self.components.decision_engine
        self.decision_validator = self.components.decision_validator
        self.decision_memory = self.components.decision_memory
        self.decision_quality = self.components.decision_quality

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

        self.strategy_lifecycle = (
            self.components.strategy_lifecycle
        )

        self.lifecycle_analytics = LifecycleAnalytics()
        
        
    def create_report(self, consensus):

        learning_insight = self.learning_analyzer.analyze(
            self.decision_memory.records
        )

        experience_context = self.experience_context.build_context( 
            strategy="Trend"
        )
        
        experience_bonus = self.experience_confidence.calculate(
            experience_context
        )

        if consensus is None:

            regime = type(
            "RegimeResult",
            (),
            {
                "regime": "UNKNOWN",
                "reasons": [],
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
                "reasons": [],
            }

        else:

            regime = self.regime_analyzer.analyze(consensus)

            risk = self.risk_analyzer.analyze(consensus)

            analysis = self.reasoning.generate(
                consensus,
                risk
            )

        
        analysis["confidence"] = self.adaptive_confidence.adjust(
            analysis["confidence"],
            learning_insight,
            experience_bonus
        )
        

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

                f"Historical Reliability: {learning_insight.reliability}",

                *regime.reasons,

                *risk.reasons,

                *analysis["reasons"]

            ]

        )
    
        report.scenarios = scenarios

        report.learning_insight = learning_insight
        
        report.experience_context = experience_context

        if hasattr(self, "evolution_history"):

            history = (
                getattr(self.evolution_history, "records", None)
                or getattr(self.evolution_history, "_records", None)
                or getattr(self.evolution_history, "history", None)
                or []
            )

            print("EVOLUTION HISTORY:", self.evolution_history.__dict__)

            print("FINAL HISTORY:", history)

            report.evolution = {
                "summary": {
                    "best_strategy": (
                        history[-1].child
                        if history
                        else None
                    )
                },
                "ranking": {
                    "rank": (
                        "EXCELLENT"
                        if history
                        and history[-1].score_after >= 90
                        else "UNKNOWN"
                    ),
                    "score": (
                        history[-1].score_after
                        if history
                        else 0
                    )
                },
                "history": history
            }

        else:

            report.evolution = {
                "summary": {
                    "best_strategy": None
                },
                "history": []
            }

                   
        best_strategy = None

        best_strategy = self.strategy_selector.select(
            report.regime,
            report.signal,
             report.risk
        )

        champion_strategy = None

        if best_strategy:

            champion_strategy = (
                self.strategy_bridge.get_best_strategy(
                    [best_strategy]
                )
            )

        report.champion_strategy = champion_strategy

        report.strategy_intelligence = None

        
        strategy_history = (
            self.strategy_history.get_history(
                best_strategy
            )
        )

        strategy_intelligence_context, strategy_knowledge = (
            self.strategy_intelligence_adapter.build_context(
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

        else:

            report.strategy_intelligence = None


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


            if evolution_permission["decision"] == "ALLOW":

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
        
        if best_strategy:  
   
            strategy_bonus = (
                self.experience_confidence
                .calculate_from_strategy(
                    best_strategy    

                )
            )

            report.strategy_context = (
                self.strategy_context.analyze(
                    report.regime,
                    report.signal,
                    report.risk
                )
            )

            report.confidence = (
                self.confidence_adjuster.adjust(
                    report.confidence,
                    strategy_bonus    
                )
            )


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

            if governance_result["status"] != "APPROVED":
                return governance_result


        decision = self.decision_engine.decide(
            report
        )


        report.decision = decision

        report.strategy_insight = self.strategy_analyzer.analyze(
            decision,
            report

        )
                       
        outcome = OutcomeRecord(
            decision=decision,
            entry_price=65000,
            exit_price=67000
        )


        report.performance_feedback = (
            self.performance_feedback.evaluate(
                outcome
            )
        )

        strategy_record = self.strategy_feedback.create_record(
            report.strategy_insight["strategy"],
            report.performance_feedback
        )

        self.strategy_performance_memory.save_performance(
            strategy_record
        )

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


        improved_strategy = self.strategy_improvement.improve(
            strategy_record.strategy,
            report.strategy_insight["score"],
            [
                strategy_record
            ]
        )

        print("IMPROVED STRATEGY:", improved_strategy)


        self.strategy_update.update(
            improved_strategy
        )

        strategy_performance = self.strategy_performance.analyze(
            self.strategy_history.get_all()
        )

        experience = ExperienceRecord(

            regime=report.regime,

            signal=report.signal,

            risk=report.risk,

            success=(
                report.performance_feedback["result"] == "SUCCESS"
            ),

            score=report.performance_feedback["score"]

        )


        self.experience_memory.save_experience(
            experience
        )

        patterns = self.pattern_intelligence.analyze(
            self.experience_memory.get_experiences()
        )


        if patterns:
            learned_strategies = self.strategy_learner.learn(
                patterns
            )

            report.learned_strategies = (
                 learned_strategies
            )    

        historical_context = HistoricalContext(

            pattern=f"{report.regime} + {decision.action}",

            confidence=learning_insight.average_confidence,

            samples=learning_insight.samples,

            reliability=learning_insight.reliability

        )


        intelligence_context = IntelligenceContext(

            learning_insight=getattr(
                 report,
                 "learning_insight",
                 None

                      
        ),

        historical_context=historical_context,

        pattern_insight=getattr(
            report,
            "pattern_insight",
            None
        ),

        quality_score=0,

        adaptive_confidence=report.confidence

        )


        report.historical_context = historical_context


        is_valid = self.decision_validator.validate(
            decision
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


        record = DecisionRecord(

            symbol=report.symbol,

            timeframe=report.timeframe,

            regime=report.regime,

            signal=report.signal,

            confidence=report.confidence,

            risk=report.risk,

            action=decision.action,

            validation_status=report.action_proposal.status

        )


        quality_result = self.decision_quality.calculate(
            record
        )


        record.quality_score = quality_result["quality_score"]


        self.decision_memory.store(record)
       
       
        
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

        report.strategy_lifecycle = None


        if best_strategy:

            lifecycle_analysis = (
                self.lifecycle_analytics.analyze(
                    best_strategy["name"],
                    self.strategy_lifecycle.history
                )
            )


            report.strategy_lifecycle = lifecycle_analysis

        report.self_evolution = {

            "status": "READY",

            "controller": (
                self.self_evolution_controller
                    is not None
            )

        }

        if hasattr(self, "evolution_history"):

            evolution_builder = EvolutionReportBuilder(

                EvolutionAnalytics(
                    self.evolution_history
            ),

            EvolutionRanker(),

            EvolutionExplainer()

        )

        evolution_report = evolution_builder.build()

        if (
            "summary" in evolution_report
            and evolution_report["summary"].get("best_strategy") is None
        ):

            history = (
                getattr(
                    self.evolution_history,
                    "_records",
                    []
                )
            )

            if history:
                evolution_report["summary"]["best_strategy"] = (
                    history[-1].child
                )


        report.evolution = evolution_report


        return report

        
    def build_report(
        self
    ):

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


            evolution_report = builder.build()

            report["evolution"] = evolution_report


        else:

            report["evolution"] = {

                "summary": {

                    "total_evolutions": 0,

                    "best_strategy": None

                },

                "ranking": {

                    "rank": "UNKNOWN",

                    "score": 0

                },

                "explanation": None

            }


        return report


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

        print("GOVERNANCE FEEDBACK:", feedback)

        confidence = (
            self.governance_confidence.calculate(
                feedback
            )
        )


        return {
            "feedback": feedback,
            "confidence": confidence
        }