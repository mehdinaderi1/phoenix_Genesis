from dataclasses import dataclass, field


@dataclass
class DecisionTrace:
    """
    Complete explainable decision execution trace.
    """

    decision: str

    signal: str

    confidence: float

    risk: str

    strategy_consensus: dict = field(
        default_factory=dict
    )

    gates: dict = field(
        default_factory=dict
    )

    explanation: dict = field(
        default_factory=dict
    )


    def to_dict(self):

        return {

            "decision":
                self.decision,

            "signal":
                self.signal,

            "confidence":
                self.confidence,

            "risk":
                self.risk,

            "strategy_consensus":
                (
                    self.strategy_consensus.to_dict()
                    if hasattr(
                        self.strategy_consensus,
                        "to_dict"
                    )
                    else self.strategy_consensus
                ),

            "gates":
                self.gates,

            "explanation":
                self.explanation
        }