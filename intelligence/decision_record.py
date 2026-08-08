from dataclasses import dataclass
from datetime import datetime, UTC


@dataclass
class DecisionRecord:

    symbol: str
    timeframe: str

    regime: str
    signal: str

    confidence: int
    risk: str

    action: str
    validation_status: str

    champion_strategy: dict | None = None

    strategy: dict | None = None

    quality_score: float = 0

    trace: dict | None = None

    timestamp: str | None = None


    def __post_init__(self):

        if self.timestamp is None:
            self.timestamp = datetime.now(UTC).isoformat()