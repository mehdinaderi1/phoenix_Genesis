from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class GovernanceRecord:

    strategy: dict

    status: str

    reason: str

    timestamp: datetime = (
        datetime.now(timezone.utc)
    )