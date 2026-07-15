from intelligence.decision_validator import DecisionValidator
from intelligence.action_proposal import ActionProposal
from intelligence.reasoning import ReasoningEngine
from intelligence.regime_analyzer import RegimeAnalyzer
from intelligence.risk_analyzer import RiskAnalyzer
from intelligence.report import MarketReport
from intelligence.decision_engine import DecisionEngine


class IntelligenceFlow:

    def __init__(self):

        self.reasoning = ReasoningEngine()
        self.regime_analyzer = RegimeAnalyzer()
        self.risk_analyzer = RiskAnalyzer()
        self.decision_engine = DecisionEngine()
        self.decision_validator = DecisionValidator()

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

        return report