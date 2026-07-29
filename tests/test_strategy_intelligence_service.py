from intelligence.strategy_intelligence_service import (
    StrategyIntelligenceService
)

from intelligence.strategy_intelligence_context import (
    StrategyIntelligenceContext
)

from intelligence.learning.strategy_evolution_knowledge import (
    StrategyKnowledge
)



def test_strategy_intelligence_service_analysis():

    context = StrategyIntelligenceContext(

        strategy="Trend",

        confidence=0.68,

        reason="Evolution validated",

        has_evolution_knowledge=True

    )


    knowledge = StrategyKnowledge(

        strategy="Trend",

        generations=5,

        average_score=85,

        average_success_rate=0.80,

        improvements=3,

        retirements=0

    )


    service = StrategyIntelligenceService()


    result = service.analyze(

        context,

        knowledge

    )


    assert result is not None

    assert result.strategy == "Trend"

    assert result.has_evolution_knowledge is True

    assert result.learning_rule == (
        "Strategy shows strong historical evolution pattern"
    )

    assert result.learning_confidence == 0.8



def test_strategy_intelligence_service_without_knowledge():

    context = StrategyIntelligenceContext(

        strategy="Scalping",

        confidence=0.6,

        reason="Current selection",

        has_evolution_knowledge=False

    )


    service = StrategyIntelligenceService()


    result = service.analyze(

        context,

        None

    )


    assert result is not None

    assert result.strategy == "Scalping"

    assert result.learning_rule is None

    assert result.learning_confidence == 0.0