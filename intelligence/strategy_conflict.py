from dataclasses import dataclass, field


@dataclass
class StrategyConflictResult:
    """
    Represents disagreement analysis
    between multiple strategies.
    """


    conflict: bool


    conflict_level: str


    dominant_action: str | None = None


    buy_support: int = 0


    sell_support: int = 0


    total_strategies: int = 0


    confidence_penalty: float = 0.0


    conflicting_strategies: list = field(
        default_factory=list
    )


    explanation: dict = field(
        default_factory=dict
    )


    def to_dict(self):

        return {

            "conflict":
                self.conflict,

            "conflict_level":
                self.conflict_level,

            "dominant_action":
                self.dominant_action,

            "buy_support":
                self.buy_support,

            "sell_support":
                self.sell_support,

            "total_strategies":
                self.total_strategies,

            "confidence_penalty":
                self.confidence_penalty,

            "conflicting_strategies":
                self.conflicting_strategies,

            "explanation":
                self.explanation
        }