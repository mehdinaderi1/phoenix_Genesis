from dataclasses import dataclass


@dataclass(slots=True)
class AdaptiveLearningContext:

    base_confidence: int

    learning_insight: object | None = None

    experience_context: dict | None = None

    pattern_insight: object | None = None

    strategy_context: object | None = None


class AdaptiveLearningContextBuilder:


    def build(
        self,
        base_confidence,
        learning_insight=None,
        experience_context=None,
        pattern_insight=None,
        strategy_context=None
    ):

        return AdaptiveLearningContext(

            base_confidence=base_confidence,

            learning_insight=learning_insight,

            experience_context=experience_context,

            pattern_insight=pattern_insight,

            strategy_context=strategy_context

        )
