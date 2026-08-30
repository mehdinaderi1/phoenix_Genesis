from dataclasses import dataclass, field
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
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )