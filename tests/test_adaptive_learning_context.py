from intelligence.adaptive_learning_context import (
    AdaptiveLearningContext
)


def test_adaptive_learning_context_contains_learning_sources():

    context = AdaptiveLearningContext(

        base_confidence=70,

        learning_insight="learning",

        experience_context={
            "total_experiences": 10,
            "successful": 8
        },

        pattern_insight="pattern",

        strategy_context="strategy"

    )


    assert context.base_confidence == 70

    assert context.learning_insight == "learning"

    assert (
        context.experience_context["successful"]
        == 8
    )

    assert context.pattern_insight == "pattern"

    assert context.strategy_context == "strategy"
