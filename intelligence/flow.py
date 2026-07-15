from intelligence.reasoning import ReasoningEngine
from intelligence.regime_analyzer import RegimeAnalyzer
from intelligence.risk_analyzer import RiskAnalyzer
from intelligence.report import MarketReport


class IntelligenceFlow:

    def __init__(self):

        self.reasoning = ReasoningEngine()
        self.regime_analyzer = RegimeAnalyzer()
        self.risk_analyzer = RiskAnalyzer()


    def create_report(self, consensus):

        regime = self.regime_analyzer.analyze(consensus)

        risk = self.risk_analyzer.analyze(consensus)

        analysis = self.reasoning.generate(consensus)

        return MarketReport(
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