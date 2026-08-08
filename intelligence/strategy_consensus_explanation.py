from dataclasses import dataclass, field


@dataclass
class StrategyConsensusExplanation:
    """
    Explainable output for multi strategy consensus.
    """

    decision: str | None

    dominant_strategy: str | None = None

    supporting_strategies: list = field(
        default_factory=list
    )

    opposing_strategies: list = field(
        default_factory=list
    )

    reasons: list[str] = field(
        default_factory=list
    )

    confidence: float = 0.0

    conflict_detected: bool = False

    metadata: dict = field(
        default_factory=dict
    )



    def to_dict(self):

        return {

            "decision":
                self.decision,

            "dominant_strategy":
                self.dominant_strategy,

            "supporting_strategies":
                self.supporting_strategies,

            "opposing_strategies":
                self.opposing_strategies,

            "reasons":
                self.reasons,

            "confidence":
                self.confidence,

            "conflict_detected":
                self.conflict_detected,

            "metadata":
                self.metadata
        }