from dataclasses import dataclass


@dataclass(slots=True)
class StrategyIntelligenceContext:

    strategy: str | None

    confidence: float

    reason: str

    has_evolution_knowledge: bool



class StrategyIntelligenceContextBuilder:


    def build(
        self,
        selection
    ):

        if selection is None:

            return StrategyIntelligenceContext(

                strategy=None,

                confidence=0.0,

                reason="No strategy selected",

                has_evolution_knowledge=False

            )


        return StrategyIntelligenceContext(

            strategy=selection.strategy,

            confidence=selection.score,

            reason=selection.reason,

            has_evolution_knowledge=True

        )