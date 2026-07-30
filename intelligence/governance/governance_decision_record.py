from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class GovernanceDecisionRecord:

    strategy: object

    decision: str

    confidence: float

    reason: str

    timestamp: datetime = None


    def __post_init__(self):

        if self.timestamp is None:

            self.timestamp = datetime.now(
                timezone.utc
            )