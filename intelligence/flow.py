from intelligence.decision_memory import DecisionMemory
from intelligence.decision_record import DecisionRecord
from intelligence.decision_validator import DecisionValidator
from intelligence.action_proposal import ActionProposal
from intelligence.reasoning import ReasoningEngine
from intelligence.regime_analyzer import RegimeAnalyzer
from intelligence.risk_analyzer import RiskAnalyzer
from intelligence.report import MarketReport
from intelligence.decision_engine import DecisionEngine
from intelligence.pattern_service import PatternService
from intelligence.historical_context import HistoricalContext
from intelligence.decision_quality import DecisionQualityAnalyzer


class IntelligenceFlow:

    def __init__(self):

        self.reasoning = ReasoningEngine()

        self.regime_analyzer = RegimeAnalyzer()

        self.risk_analyzer = RiskAnalyzer()

        self.decision_engine = DecisionEngine()

        self.decision_validator = DecisionValidator()

        self.decision_memory = DecisionMemory()

        self.pattern_service = PatternService()

        self.decision_quality = DecisionQualityAnalyzer()


    def create_report(self, consensus):

        regime = self.regime_analyzer.analyze(consensus)


        risk = self.risk_analyzer.analyze(consensus)


        analysis = self.reasoning.generate(
            consensus,
            risk
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

                *regime.reasons,

                *risk.reasons,

                *analysis["reasons"]

            ]

        )


        decision = self.decision_engine.decide(
            report
        )


        report.decision = decision


        historical_context = HistoricalContext(

            pattern=f"{report.regime} + {decision.action}",

            confidence=0,

            samples=0,

            reliability="UNKNOWN"

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

            validation_status=report.action_proposal.status,
            
        )

        quality_result = self.decision_quality.calculate(
            record
            
        )

        record.quality_score = quality_result["quality_score"]

        self.decision_memory.store(record)


        return report