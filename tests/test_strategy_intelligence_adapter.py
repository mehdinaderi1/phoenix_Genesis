from intelligence.strategy_intelligence_adapter import (
    StrategyIntelligenceAdapter
)

from intelligence.learning.strategy_evolution_history import (
    EvolutionRecord
)


def test_strategy_intelligence_adapter_with_history():

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


    assert context is not None

    assert knowledge is not None


    assert knowledge.strategy == "Trend"

    assert knowledge.generations == 2

    assert knowledge.average_score == 80

    assert knowledge.average_success_rate == 0.75


    assert knowledge.improvements == 1

    assert knowledge.retirements == 0


    assert context.has_evolution_knowledge is True



def test_strategy_intelligence_adapter_without_history():

    adapter = StrategyIntelligenceAdapter()


    context, knowledge = adapter.build_context(

        "Trend",

        []

    )


    assert context is not None

    assert knowledge is None


    assert context.strategy == "Trend"

    assert context.has_evolution_knowledge is False

    assert context.reason == "No evolution history"



def test_strategy_intelligence_adapter_without_strategy():

    adapter = StrategyIntelligenceAdapter()


    context, knowledge = adapter.build_context(

        None,

        []

    )


    assert context is None

    assert knowledge is None