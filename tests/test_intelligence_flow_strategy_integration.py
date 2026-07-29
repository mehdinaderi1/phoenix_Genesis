from intelligence.strategy_intelligence_adapter import (
    StrategyIntelligenceAdapter
)

from intelligence.strategy_intelligence_service import (
    StrategyIntelligenceService
)

from intelligence.learning.strategy_evolution_history import (
    EvolutionRecord
)


def test_strategy_intelligence_full_integration():

    history = [

        EvolutionRecord(

            strategy="Trend",

            parent=None,

            generation=1,

            decision="IMPROVE",

            reason="Need optimization",

            score=70,

            success_rate=0.65

        ),

        EvolutionRecord(

            strategy="Trend_v2",

            parent="Trend",

            generation=2,

            decision="KEEP",

            reason="Good performance",

            score=90,

            success_rate=0.85

        )

    ]


    adapter = StrategyIntelligenceAdapter()


    context, knowledge = adapter.build_context(

        "Trend",

        history

    )


    service = StrategyIntelligenceService()


    result = service.analyze(

        context,

        knowledge

    )


    assert result is not None

    assert result.strategy == "Trend"

    assert result.has_evolution_knowledge is True

    assert result.learning_confidence > 0



def test_strategy_intelligence_safe_without_history():

    adapter = StrategyIntelligenceAdapter()


    context, knowledge = adapter.build_context(

        "Trend",

        []

    )


    service = StrategyIntelligenceService()


    result = service.analyze(

        context,

        knowledge

    )


    assert result is not None

    assert result.strategy == "Trend"

    assert result.has_evolution_knowledge is False

    assert result.learning_confidence == 0.0