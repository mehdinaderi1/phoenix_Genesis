from dataclasses import dataclass


@dataclass(frozen=True)
class MarketData:
    """Normalized market data shared by Phoenix market-data sources."""

    symbol: str
    price: float
    source: str
    fallback_used: bool = False
    source_status: str = "HEALTHY"
