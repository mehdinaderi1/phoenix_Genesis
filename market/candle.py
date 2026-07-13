from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class Candle:

    symbol: str
    timeframe: str
    timestamp: int

    open: float
    high: float
    low: float
    close: float
    volume: float

    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self):
        return {
            "symbol": self.symbol,
            "timeframe": self.timeframe,
            "timestamp": self.timestamp,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
            "created_at": self.created_at
        }