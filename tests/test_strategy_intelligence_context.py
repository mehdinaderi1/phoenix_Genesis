from intelligence.strategy_intelligence_context import (
    StrategyIntelligenceContextBuilder
)

from intelligence.learning.strategy_intelligence_selector import (
    IntelligenceSelection
)


def test_build_strategy_intelligence_context():

    selection = IntelligenceSelection(

        strategy="Trend",

        score=0.68,

        reason="Current strategy validated by evolution knowledge"

    )


    builder = StrategyIntelligenceContextBuilder()


    context = builder.build(

        selection

    )


    assert context is not None

    assert context.strategy == "Trend"

    assert context.confidence == 0.68

    assert (
        context.reason
        ==
        "Current strategy validated by evolution knowledge"
    )

    assert context.has_evolution_knowledge is True



def test_empty_selection_returns_safe_context():

    builder = StrategyIntelligenceContextBuilder()


    context = builder.build(

        None

    )


    assert context is not None

    assert context.strategy is None

    assert context.confidence == 0.0

    assert context.reason == "No strategy selected"

    assert context.has_evolution_knowledge is False