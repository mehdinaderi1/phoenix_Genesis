from dataclasses import dataclass, field


@dataclass
class ActionProposal:
    """
    Explainable action proposal generated
    from validated decision.
    """

    action: str | None = None

    status: str = "PENDING"

    reason: str = ""

    confidence: float = 0.0

    symbol: str | None = None

    strategy: str | None = None

    risk_status: str = "UNKNOWN"

    metadata: dict = field(
        default_factory=dict
    )


    def to_dict(self):

        return {

            "action":
                self.action,

            "status":
                self.status,

            "reason":
                self.reason,

            "confidence":
                self.confidence,

            "symbol":
                self.symbol,

            "strategy":
                self.strategy,

            "risk_status":
                self.risk_status,

            "metadata":
                self.metadata
        }