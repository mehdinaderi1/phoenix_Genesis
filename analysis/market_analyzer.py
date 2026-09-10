from analysis.technical_engine import TechnicalEngine
from analysis.signal_engine import SignalEngine
from analysis.confidence_engine import ConfidenceEngine


class MarketAnalyzer:

    def __init__(self):

        self.technical = TechnicalEngine()
        self.signal_engine = SignalEngine()
        self.confidence_engine = ConfidenceEngine()

    def analyze(self, prices):

        ma = self.technical.calculate_ma(
            prices,
            5
        )

        rsi = self.technical.calculate_rsi(
            prices,
            14
        )

        macd = self.technical.calculate_macd(
            prices
        )

        indicators = {
            "ma": ma,
            "rsi": rsi,
            "macd": macd
        }

        current_price = prices[-1] if prices else None

        signals = self.signal_engine.analyze(
            indicators,
            current_price
        )

        confidence = self.confidence_engine.calculate(
            signals
        )

        return {
            # Existing contract
            "ma": ma,
            "rsi": rsi,
            "macd": macd,

            # New analysis information
            "indicators": indicators,
            "signals": signals,
            "confidence": confidence
        }