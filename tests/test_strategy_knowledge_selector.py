from intelligence.learning.strategy_evolution_knowledge import (
    StrategyKnowledge
)

from intelligence.learning.strategy_knowledge_selector import (
    StrategyKnowledgeSelector
)


def test_select_best_strategy_by_evolution_knowledge():

    knowledge_list = [

        StrategyKnowledge(

            strategy="Trend",

            generations=3,

            average_score=85,

            average_success_rate=0.80,

            improvements=2,

            retirements=0

        ),

        StrategyKnowledge(

            strategy="Scalping",

            generations=4,

            average_score=70,

            average_success_rate=0.90,

            improvements=3,

            retirements=1

        )

    ]


    selector = StrategyKnowledgeSelector()


    result = selector.select(

        knowledge_list

    )


    assert result is not None

    assert result.strategy == "Trend"

    assert result.reason == (
        "Highest historical evolution performance"
    )



def test_empty_knowledge_returns_none():

    selector = StrategyKnowledgeSelector()


    result = selector.select([])


    assert result is None