from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class MarketObservation:
    symbol: str
    price: float | None
    source: str | None
    fallback_used: bool
    source_status: str
    observation_number: int
    timestamp: str


class RealMarketObserver:

    def __init__(self, source_manager):
        if source_manager is None:
            raise ValueError("source_manager must not be None")

        self.source_manager = source_manager
        self.observation_count = 0

    def observe(self, symbol="BTCUSDT"):
        self.observation_count += 1
        timestamp = datetime.now(timezone.utc).isoformat()

        try:
            market_data = self.source_manager.get_price(symbol)
        except RuntimeError:
            return MarketObservation(
                symbol=symbol,
                price=None,
                source=None,
                fallback_used=False,
                source_status="BLIND",
                observation_number=self.observation_count,
                timestamp=timestamp,
            )

        return MarketObservation(
            symbol=market_data.symbol,
            price=market_data.price,
            source=market_data.source,
            fallback_used=market_data.fallback_used,
            source_status=market_data.source_status,
            observation_number=self.observation_count,
            timestamp=timestamp,
        )
