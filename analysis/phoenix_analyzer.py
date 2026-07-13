from analysis.signal_engine import SignalEngine
from analysis.confidence_engine import ConfidenceEngine
from analysis.decision_engine import DecisionEngine
from analysis.risk_engine import RiskEngine
from analysis.report_generator import ReportGenerator


class PhoenixAnalyzer:

    def __init__(self):

        self.signal_engine = SignalEngine()
        self.confidence_engine = ConfidenceEngine()
        self.decision_engine = DecisionEngine()
        self.risk_engine = RiskEngine()
        self.report_generator = ReportGenerator()


    def run(self, asset):

       # مرحله ۱ - تحلیل سیگنال
        indicators = {
        "ma": 70740,
        "rsi": 100,
        "macd": 1745.28
        }

        signals = self.signal_engine.analyze(
            indicators
        )


        # مرحله ۲ - اعتماد تحلیل
        confidence = self.confidence_engine.calculate(
            signals
        )


        # مرحله ۳ - تصمیم
        decision = self.decision_engine.decide(
            confidence,
            signals
        )


        # مرحله ۴ - ریسک
        risk = self.risk_engine.analyze(
            confidence,
            signals
        )


        # مرحله ۵ - گزارش نهایی
        report = self.report_generator.generate(
            asset,
            signals,
            confidence,
            decision["decision"],
            risk["risk"]
        )


        report["warnings"] = risk["warnings"]

        return report