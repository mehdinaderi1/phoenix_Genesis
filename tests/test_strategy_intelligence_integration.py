from intelligence.strategy_intelligence_service import (
    StrategyIntelligenceService
)

from intelligence.strategy_intelligence_context import (
    StrategyIntelligenceContext
)

from intelligence.learning.strategy_evolution_knowledge import (
    StrategyKnowledge
)


def test_strategy_intelligence_integration_flow():

    strategy_context = StrategyIntelligenceContext(

        strategy="Trend",

        confidence=0.75,

        reason="Selected from evolution knowledge",

        has_evolution_knowledge=True

    )


    knowledge = StrategyKnowledge(

        strategy="Trend",

        generations=6,

        average_score=88,

        average_success_rate=0.82,

        improvements=4,

        retirements=0

    )


    service = StrategyIntelligenceService()


    result = service.analyze(

        strategy_context,

        knowledge

    )


    assert result is not None

    assert result.strategy == "Trend"

    assert result.has_evolution_knowledge is True

    assert result.learning_rule is not None

    assert result.learning_confidence > 0



def test_strategy_intelligence_without_learning_data():

    strategy_context = StrategyIntelligenceContext(

        strategy="Trend",

        confidence=0.7,

        reason="Current strategy",

        has_evolution_knowledge=False

    )


    service = StrategyIntelligenceService()


    result = service.analyze(

        strategy_context,

        None

    )


    assert result.strategy == "Trend"

    assert result.learning_rule is None

    assert result.learning_confidence == 0.0