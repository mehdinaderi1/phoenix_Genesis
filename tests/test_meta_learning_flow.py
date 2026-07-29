from intelligence.strategy_intelligence_context import (
    StrategyIntelligenceContext
)

from intelligence.learning.strategy_evolution_knowledge import (
    StrategyKnowledge
)

from intelligence.learning.meta_learning_flow import (
    MetaLearningFlow
)



def test_meta_learning_full_flow():

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


    flow = MetaLearningFlow()


    result = flow.run(

        context,

        knowledge

    )


    assert result is not None

    assert result.strategy == "Trend"

    assert result.learning_rule == (
        "Strategy shows strong historical evolution pattern"
    )

    assert result.learning_confidence == 0.8

    assert result.has_evolution_knowledge is True