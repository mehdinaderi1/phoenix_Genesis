from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class GovernanceRecord:

    strategy: dict

    status: str

    reason: str

    result: str = None

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        )
    )


    def __getitem__(
        self,
        key
    ):

        return getattr(
            self,
            key
        )


    def get(
        self,
        key,
        default=None
    ):

        return getattr(
            self,
            key,
            default
        )


    def to_dict(
        self
    ):

        return {
            "strategy": self.strategy,
            "status": self.status,
            "reason": self.reason,
            "result": self.result,
            "timestamp": self.timestamp
        }