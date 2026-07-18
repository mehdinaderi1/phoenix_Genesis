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
from intelligence.experience_record import ExperienceRecord
from intelligence.experience_context import ExperienceContext
from intelligence.memory.experience_memory import ExperienceMemory
from intelligence.experience_confidence import ExperienceConfidence
from intelligence.confidence_adjuster import ConfidenceAdjuster
from intelligence.pattern_intelligence import PatternIntelligence
from intelligence.strategy_memory import StrategyMemory
from intelligence.strategy_analyzer import StrategyAnalyzer
from intelligence.strategy_recall import StrategyRecall
from intelligence.strategy_context import StrategyContext
from intelligence.strategy_feedback import StrategyFeedback
from intelligence.strategy_selector import StrategySelector
from intelligence.strategy_selector import StrategySelector
from intelligence.strategy_learner import StrategyLearner
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


class IntelligenceFlow:

    def __init__(self):

        self.reasoning = ReasoningEngine()

        self.regime_analyzer = RegimeAnalyzer()

        self.risk_analyzer = RiskAnalyzer()

        self.decision_engine = DecisionEngine()

        self.decision_validator = DecisionValidator()

        self.decision_memory = DecisionMemory()

        self.pattern_service = PatternService()

        self.pattern_intelligence = PatternIntelligence()

        self.decision_quality = DecisionQualityAnalyzer()

        self.scenario_engine = ScenarioEngine()

        self.learning_analyzer = LearningAnalyzer()

        self.adaptive_confidence = AdaptiveConfidence()

        self.experience_confidence = ExperienceConfidence()

        self.strategy_analyzer = StrategyAnalyzer()

        self.strategy_history = StrategyHistory()

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
            StrategyRanker()
        )
                    

        self.strategy_context = StrategyContext(
            self.strategy_recall
        )

        self.confidence_adjuster = ConfidenceAdjuster()

        self.strategy_quality_gate = StrategyQualityGate()

        self.performance_feedback = PerformanceFeedback()

        self.strategy_feedback = StrategyFeedback()

        self.strategy_improvement = StrategyImprovementEngine()

        self.strategy_history = StrategyHistory()


        self.strategy_update = StrategyUpdate(
            self.strategy_memory,
            self.strategy_quality_gate,
            self.strategy_history
        )    

        self.experience_memory = ExperienceMemory()

        self.experience_context = ExperienceContext(
            self.experience_memory
        )
       
        self.experience_confidence = ExperienceConfidence()

        

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
                
        report = MarketReport(

            symbol="BTCUSDT",

            timeframe="Multi",

            trend=consensus.trend,

            regime=regime.regime,

            signal=analysis["signal"],

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

        best_strategy = None

        best_strategy = self.strategy_selector.select(
            report.regime,
            report.signal,
             report.risk
        )

        strategy_history = (
            self.strategy_history.get_history(
                best_strategy
            )
        )


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

        decision = self.decision_engine.decide(
            report
        )


        report.decision = decision

        report.strategy_insight = self.strategy_analyzer.analyze(
            decision,
            report

        )
                       
        report.performance_feedback = self.performance_feedback.evaluate(
           decision,
           65000,
           67000 
        )

        strategy_record = self.strategy_feedback.create_record(
            report.strategy_insight["strategy"],
            report.performance_feedback
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

        return report