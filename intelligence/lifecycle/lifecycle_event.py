from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class LifecycleEvent:

    strategy_name: str

    from_state: str

    to_state: str

    reason: str

    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


    def to_dict(self):

        return {

            "strategy_name": self.strategy_name,

            "from_state": self.from_state,

            "to_state": self.to_state,

            "reason": self.reason,

            "created_at": self.created_at.isoformat()

        }