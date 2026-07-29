import pytest


from intelligence.strategy_confidence_influence import (
    StrategyConfidenceInfluencer
)


class MockStrategyIntelligence:

    def __init__(
        self,
        has_evolution_knowledge,
        learning_confidence
    ):

        self.has_evolution_knowledge = (
            has_evolution_knowledge
        )

        self.learning_confidence = (
            learning_confidence
        )



def test_strong_strategy_intelligence_increases_confidence():

    influencer = StrategyConfidenceInfluencer()


    intelligence = MockStrategyIntelligence(

        has_evolution_knowledge=True,

        learning_confidence=0.85

    )


    result = influencer.influence(

        0.70,

        intelligence

    )


    assert result.confidence == pytest.approx(0.80)

    assert result.adjustment == 0.10

    assert (
        result.reason
        ==
        "Strong strategy evolution confidence"
    )



def test_moderate_strategy_intelligence_increases_confidence():

    influencer = StrategyConfidenceInfluencer()


    intelligence = MockStrategyIntelligence(

        has_evolution_knowledge=True,

        learning_confidence=0.60

    )


    result = influencer.influence(

        0.70,

        intelligence

    )


    assert result.confidence == pytest.approx(0.75)

    assert result.adjustment == 0.05

    assert (
        result.reason
        ==
        "Moderate strategy evolution confidence"
    )



def test_no_strategy_intelligence_keeps_confidence():

    influencer = StrategyConfidenceInfluencer()


    result = influencer.influence(

        0.70,

        None

    )


    assert result.confidence == pytest.approx(0.70)

    assert result.adjustment == 0.0

    assert (
        result.reason
        ==
        "No strategy intelligence"
    )



def test_without_evolution_knowledge_keeps_confidence():

    influencer = StrategyConfidenceInfluencer()


    intelligence = MockStrategyIntelligence(

        has_evolution_knowledge=False,

        learning_confidence=0.90

    )


    result = influencer.influence(

        0.70,

        intelligence

    )


    assert result.confidence == 0.70

    assert result.adjustment == 0.0

    assert (
        result.reason
        ==
        "No evolution knowledge"
    )