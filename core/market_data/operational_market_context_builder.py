from datetime import datetime, timezone

from core.market_data.operational_market_context import OperationalMarketContext


class OperationalMarketContextBuilder:
    def build(self, symbol, consensus):
        if consensus is None:
            raise ValueError("consensus must not be None")

        return OperationalMarketContext(
            symbol=symbol,
            trend=consensus.trend,
            signal=consensus.signal,
            confidence=consensus.confidence,
            timestamp=datetime.now(timezone.utc).isoformat()
        )
