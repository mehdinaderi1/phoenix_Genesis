from intelligence.strategy_intelligence_service import (
    StrategyIntelligenceService
)

from intelligence.strategy_intelligence_context import (
    StrategyIntelligenceContext
)

from intelligence.learning.strategy_evolution_knowledge import (
    StrategyKnowledge
)


def test_intelligence_flow_with_strategy_intelligence_context():

    strategy_context = StrategyIntelligenceContext(

        strategy="Trend",

        confidence=0.78,

        reason="Validated by evolution history",

        has_evolution_knowledge=True

    )


    knowledge = StrategyKnowledge(

        strategy="Trend",

        generations=7,

        average_score=90,

        average_success_rate=0.85,

        improvements=5,

        retirements=0

    )


    service = StrategyIntelligenceService()


    enhanced_context = service.analyze(

        strategy_context,

        knowledge

    )


    assert enhanced_context is not None

    assert enhanced_context.strategy == "Trend"

    assert enhanced_context.has_evolution_knowledge is True

    assert enhanced_context.learning_rule is not None

    assert (
        enhanced_context.learning_confidence
        ==
        0.8
    )



def test_intelligence_flow_without_strategy_learning():

    strategy_context = StrategyIntelligenceContext(

        strategy="MeanReversion",

        confidence=0.65,

        reason="Selected by current analysis",

        has_evolution_knowledge=False

    )


    service = StrategyIntelligenceService()


    enhanced_context = service.analyze(

        strategy_context,

        None

    )


    assert enhanced_context is not None

    assert enhanced_context.strategy == "MeanReversion"

    assert enhanced_context.learning_rule is None

    assert enhanced_context.learning_confidence == 0.0