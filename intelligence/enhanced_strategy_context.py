from dataclasses import dataclass


@dataclass(slots=True)
class EnhancedStrategyContext:

    strategy: str | None

    confidence: float

    reason: str

    has_evolution_knowledge: bool

    learning_rule: str | None

    learning_confidence: float



class EnhancedStrategyContextBuilder:


    def build(
        self,
        strategy_context,
        meta_insight
    ):

        if strategy_context is None:

            return EnhancedStrategyContext(

                strategy=None,

                confidence=0.0,

                reason="No strategy context",

                has_evolution_knowledge=False,

                learning_rule=None,

                learning_confidence=0.0

            )


        if meta_insight is None:

            return EnhancedStrategyContext(

                strategy=strategy_context.strategy,

                confidence=strategy_context.confidence,

                reason=strategy_context.reason,

                has_evolution_knowledge=(
                    strategy_context.has_evolution_knowledge
                ),

                learning_rule=None,

                learning_confidence=0.0

            )


        return EnhancedStrategyContext(

            strategy=strategy_context.strategy,

            confidence=strategy_context.confidence,

            reason=strategy_context.reason,

            has_evolution_knowledge=(
                strategy_context.has_evolution_knowledge
            ),

            learning_rule=meta_insight.rule,

            learning_confidence=(
                meta_insight.confidence
            )

        )