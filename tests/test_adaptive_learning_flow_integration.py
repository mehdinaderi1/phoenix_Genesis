from intelligence.flow import IntelligenceFlow

from intelligence.consensus import ConsensusResult

from intelligence.adaptive_learning_context import (
    AdaptiveLearningContext
)


class SpyAdaptiveIntelligence:

    def __init__(self):

        self.context_received = None


    def adjust_context_confidence(
        self,
        context
    ):

        self.context_received = context

        return context.base_confidence


    def adjust_analysis_confidence(
        self,
        base_confidence,
        learning_insight,
        experience_context
    ):

        return base_confidence


def test_flow_builds_adaptive_learning_context():

    flow = IntelligenceFlow()

    spy = SpyAdaptiveIntelligence()

    flow.adaptive_intelligence = spy


    report = flow.create_report(

        ConsensusResult(
            trend="BULLISH",
            signal="BUY",
            confidence=85
        )

    )


    assert report is not None

    assert spy.context_received is not None

    assert isinstance(
        spy.context_received,
        AdaptiveLearningContext
    )

    assert (
        spy.context_received.base_confidence
        >= 0
    )

    assert (
        spy.context_received.learning_insight
        is not None
    )

    assert (
        spy.context_received.experience_context
        is not None
    )
