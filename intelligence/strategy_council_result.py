from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class StrategyCouncilResult:

    strategies: list = field(default_factory=list)

    strategy_votes: list = field(default_factory=list)

    consensus_action: str | None = None

    consensus_confidence: float = 0.0

    supporting_strategies: list = field(
        default_factory=list
    )

    conflicting_strategies: list = field(
        default_factory=list
    )

    strategy_weights: dict = field(
        default_factory=dict
    )

    weighted_support: dict = field(
        default_factory=dict
    )

    top_strategy: str | None = None

    explanation: str = ""

    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


    def __getitem__(self, key):

        mapping = {

            "decision":
                self.consensus_action,

            "confidence":
                self.consensus_confidence,

            "top_strategy":
                self.top_strategy,

            "supporting_strategies":
                len(self.supporting_strategies),

            "opposing_strategies":
                len(self.conflicting_strategies),

            "strategy_votes":
                self.strategy_votes,

            "strategy_weights":
                getattr(
                    self,
                    "strategy_weights",
                    {}
                ),

            "weighted_support":
                getattr(
                    self,
                    "weighted_support",
                    {})
        }


        return mapping[key]


    def get(
        self,
        key,
        default=None
    ):

        try:

            return self[key]

        except KeyError:

            return default


    def to_dict(self):

        return {
            "strategies": self.strategies,
            "strategy_votes": self.strategy_votes,
            "strategy_weights": self.strategy_weights,
            "weighted_support": self.weighted_support,
            "consensus_action": self.consensus_action,
            "consensus_confidence": self.consensus_confidence,
            "supporting_strategies": self.supporting_strategies,
            "conflicting_strategies": self.conflicting_strategies,
            "top_strategy": self.top_strategy,
            "explanation": self.explanation,
            "top_strategy": self.top_strategy,
            "timestamp": self.timestamp.isoformat()
            
        }

            