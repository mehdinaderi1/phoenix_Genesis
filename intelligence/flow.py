from intelligence.reasoning import ReasoningEngine
from intelligence.report import MarketReport


class IntelligenceFlow:

    def __init__(self):

        self.reasoning = ReasoningEngine()


    def create_report(self, consensus):

        analysis = self.reasoning.generate(consensus)

        return MarketReport(
            symbol="BTCUSDT",
            timeframe="Multi",
            trend=consensus.trend,
            signal=analysis["signal"],
            confidence=analysis["confidence"],
            risk=analysis["risk"],
            reasons=analysis["reasons"]
        )