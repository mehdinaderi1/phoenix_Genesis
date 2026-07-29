from intelligence.learning.strategy_evolution_knowledge import (
    StrategyKnowledge
)

from intelligence.learning.meta_learning_engine import (
    MetaLearningEngine
)


def test_meta_learning_detects_strong_strategy_pattern():

    knowledge = StrategyKnowledge(

        strategy="Trend",

        generations=5,

        average_score=85,

        average_success_rate=0.80,

        improvements=3,

        retirements=0

    )


    engine = MetaLearningEngine()


    insight = engine.analyze(

        knowledge

    )


    assert insight is not None

    assert insight.strategy == "Trend"

    assert insight.confidence == 0.8

    assert (
        insight.rule
        ==
        "Strategy shows strong historical evolution pattern"
    )

    assert insight.evidence == 5



def test_meta_learning_detects_weak_strategy():

    knowledge = StrategyKnowledge(

        strategy="Scalping",

        generations=2,

        average_score=40,

        average_success_rate=0.50,

        improvements=1,

        retirements=1

    )


    engine = MetaLearningEngine()


    insight = engine.analyze(

        knowledge

    )


    assert insight is not None

    assert insight.strategy == "Scalping"

    assert insight.confidence == 0.5

    assert (
        insight.rule
        ==
        "Strategy requires further improvement"
    )



def test_meta_learning_without_knowledge_returns_none():

    engine = MetaLearningEngine()


    insight = engine.analyze(

        None

    )


    assert insight is None