from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class ExperienceRecord:
    symbol: str
    strategy: str
    regime: str
    signal: str
    confidence: float
    outcome: str
    profit_loss: float
    lesson: str
    timestamp: datetime = datetime.now(timezone.utc)