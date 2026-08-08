from dataclasses import dataclass, field


@dataclass
class DecisionResult:

    action: str

    reason: str

    confidence: float

    consensus_confidence: float = 0.0

    supporting_strategies: int = 0

    opposing_strategies: int = 0

    top_strategy: str | None = None

    explanation: dict = field(
        default_factory=dict
    )

    metadata: dict = field(
        default_factory=dict
    )



    def to_dict(
        self
    ):

        return {

            "action":
                self.action,

            "reason":
                self.reason,

            "confidence":
                self.confidence,

            "consensus_confidence":
                self.consensus_confidence,

            "supporting_strategies":
                self.supporting_strategies,

            "opposing_strategies":
                self.opposing_strategies,

            "top_strategy":
                self.top_strategy,

            "explanation":
                self.explanation,

            "metadata":
                self.metadata
        }