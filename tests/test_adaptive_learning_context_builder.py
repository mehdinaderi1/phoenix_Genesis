from intelligence.adaptive_learning_context import (
    AdaptiveLearningContext,
    AdaptiveLearningContextBuilder
)


def test_adaptive_learning_context_builder_builds_context():

    builder = AdaptiveLearningContextBuilder()

    learning_insight = "learning"

    experience_context = {
        "total_experiences": 10,
        "successful": 8
    }

    pattern_insight = "pattern"

    strategy_context = "strategy"


    context = builder.build(

        base_confidence=70,

        learning_insight=learning_insight,

        experience_context=experience_context,

        pattern_insight=pattern_insight,

        strategy_context=strategy_context

    )


    assert isinstance(
        context,
        AdaptiveLearningContext
    )

    assert context.base_confidence == 70

    assert context.learning_insight == "learning"

    assert context.experience_context == experience_context

    assert context.pattern_insight == "pattern"

    assert context.strategy_context == "strategy"
