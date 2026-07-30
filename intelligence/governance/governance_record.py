from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class GovernanceRecord:

    strategy: dict

    status: str

    reason: str

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        )
    )