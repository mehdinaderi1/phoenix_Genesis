from dataclasses import dataclass, field


@dataclass
class MarketReport:

    symbol: str

    # legacy decision contract
    timeframe: str = ""
    signal: str = ""
    risk: str = ""
    reasons: list = field(default_factory=list)

    # current intelligence contract
    trend: str = ""
    momentum: str = ""
    regime: str = ""

    risk_level: str = ""

    confidence: float = 0

    reasoning: str = ""

    strategy_consensus: dict = field(
        default_factory=dict
    )


    def __post_init__(self):

        # risk compatibility

        if not self.risk and self.risk_level:
            self.risk = self.risk_level

        if not self.risk_level and self.risk:
            self.risk_level = self.risk


        # reasoning compatibility

        if not self.reasoning and self.reasons:
            self.reasoning = " ".join(
                self.reasons
            )


    def summary(self):

        return {
            "symbol": self.symbol,
            "trend": self.trend,
            "momentum": self.momentum,
            "regime": self.regime,
            "risk_level": self.risk_level,
            "confidence": self.confidence,
            "reasoning": self.reasoning
        }