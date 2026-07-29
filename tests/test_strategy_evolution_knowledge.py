from intelligence.learning.strategy_evolution_history import (
    StrategyEvolutionHistory,
    EvolutionRecord
)

from intelligence.learning.strategy_evolution_knowledge import (
    StrategyEvolutionKnowledge
)


def test_strategy_knowledge_analysis():

    history = StrategyEvolutionHistory()


    history.add(

        EvolutionRecord(

            strategy="Trend",

            parent=None,

            generation=1,

            decision="IMPROVE",

            reason="Need optimization",

            score=70,

            success_rate=0.65

        )

    )


    history.add(

        EvolutionRecord(

            strategy="Trend",

            parent="Trend",

            generation=2,

            decision="KEEP",

            reason="Good performance",

            score=85,

            success_rate=0.82

        )

    )


    knowledge_engine = StrategyEvolutionKnowledge(

        history

    )


    knowledge = knowledge_engine.analyze(

        "Trend"

    )


    assert knowledge is not None


    assert knowledge.strategy == "Trend"


    assert knowledge.generations == 2


    assert knowledge.average_score == 77.5


    assert knowledge.average_success_rate == 0.73


    assert knowledge.improvements == 1


    assert knowledge.retirements == 0



def test_unknown_strategy_returns_none():

    history = StrategyEvolutionHistory()


    knowledge_engine = StrategyEvolutionKnowledge(

        history

    )


    knowledge = knowledge_engine.analyze(

        "Unknown"

    )


    assert knowledge is None