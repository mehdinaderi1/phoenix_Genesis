from intelligence.reasoning import ReasoningEngine
from intelligence.regime_analyzer import RegimeAnalyzer
from intelligence.report import MarketReport


class IntelligenceFlow:

    def __init__(self):

        self.reasoning = ReasoningEngine()
        self.regime_analyzer = RegimeAnalyzer()


    def create_report(self, consensus):

        regime = self.regime_analyzer.analyze(consensus)

        analysis = self.reasoning.generate(consensus)

        return MarketReport(
            symbol="BTCUSDT",
            timeframe="Multi",
            trend=consensus.trend,
            signal=analysis["signal"],
            confidence=analysis["confidence"],
            risk=analysis["risk"],
            reasons=[
                f"Market Regime: {regime.regime}",
                *regime.reasons,
                *analysis["reasons"]
            ]
        )