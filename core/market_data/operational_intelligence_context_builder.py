from core.market_data.operational_intelligence_context import OperationalIntelligenceContext


class OperationalIntelligenceContextBuilder:
    def build(self, market_context):
        if market_context is None:
            raise ValueError("market_context must not be None")

        return OperationalIntelligenceContext(
            symbol=market_context.symbol,
            trend=market_context.trend,
            signal=market_context.signal,
            confidence=market_context.confidence
        )
