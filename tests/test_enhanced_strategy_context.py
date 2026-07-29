from intelligence.strategy_intelligence_context import (
    StrategyIntelligenceContext
)

from intelligence.learning.meta_learning_engine import (
    MetaLearningInsight
)

from intelligence.enhanced_strategy_context import (
    EnhancedStrategyContextBuilder
)


def test_build_enhanced_strategy_context_with_learning():

    strategy_context = StrategyIntelligenceContext(

        strategy="Trend",

        confidence=0.68,

        reason="Current strategy validated by evolution knowledge",

        has_evolution_knowledge=True

    )


    meta_insight = MetaLearningInsight(

        strategy="Trend",

        confidence=0.8,

        rule=(
            "Strategy shows strong "
            "historical evolution pattern"
        ),

        evidence=5

    )


    builder = EnhancedStrategyContextBuilder()


    result = builder.build(

        strategy_context,

        meta_insight

    )


    assert result is not None

    assert result.strategy == "Trend"

    assert result.confidence == 0.68

    assert result.has_evolution_knowledge is True

    assert (
        result.learning_rule
        ==
        "Strategy shows strong historical evolution pattern"
    )

    assert result.learning_confidence == 0.8



def test_build_enhanced_context_without_learning():

    strategy_context = StrategyIntelligenceContext(

        strategy="Scalping",

        confidence=0.6,

        reason="Selected by current performance",

        has_evolution_knowledge=False

    )


    builder = EnhancedStrategyContextBuilder()


    result = builder.build(

        strategy_context,

        None

    )


    assert result is not None

    assert result.strategy == "Scalping"

    assert result.learning_rule is None

    assert result.learning_confidence == 0.0



def test_build_without_strategy_context():

    builder = EnhancedStrategyContextBuilder()


    result = builder.build(

        None,

        None

    )


    assert result is not None

    assert result.strategy is None

    assert result.confidence == 0.0

    assert result.reason == "No strategy context"

    assert result.has_evolution_knowledge is False