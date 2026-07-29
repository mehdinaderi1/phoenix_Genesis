from intelligence.learning.strategy_evolution_knowledge import (
    StrategyKnowledge
)

from intelligence.learning.strategy_knowledge_selector import (
    StrategyKnowledgeSelector
)

from intelligence.learning.strategy_intelligence_selector import (
    StrategyIntelligenceSelector
)


def test_intelligence_selector_uses_evolution_knowledge():

    knowledge_list = [

        StrategyKnowledge(

            strategy="Trend",

            generations=3,

            average_score=85,

            average_success_rate=0.80,

            improvements=2,

            retirements=0

        )

    ]


    knowledge_selector = StrategyKnowledgeSelector()


    intelligence_selector = StrategyIntelligenceSelector(

        knowledge_selector

    )


    strategies = [

        {

            "name": "Scalping",

            "score": 90

        },

        {

            "name": "Trend",

            "score": 75

        }

    ]


    result = intelligence_selector.select(

        strategies,

        knowledge_list

    )


    assert result is not None

    assert result.strategy == "Trend"

    assert (
        result.reason
        ==
        "Current strategy validated by evolution knowledge"
    )



def test_intelligence_selector_fallback_to_current_score():

    knowledge_selector = StrategyKnowledgeSelector()


    intelligence_selector = StrategyIntelligenceSelector(

        knowledge_selector

    )


    strategies = [

        {

            "name": "Scalping",

            "score": 90

        },

        {

            "name": "Trend",

            "score": 75

        }

    ]


    result = intelligence_selector.select(

        strategies,

        []

    )


    assert result is not None

    assert result.strategy == "Scalping"

    assert (
        result.reason
        ==
        "Selected by current performance"
    )



def test_empty_strategies_returns_none():

    knowledge_selector = StrategyKnowledgeSelector()


    intelligence_selector = StrategyIntelligenceSelector(

        knowledge_selector

    )


    result = intelligence_selector.select(

        [],

        []

    )


    assert result is None