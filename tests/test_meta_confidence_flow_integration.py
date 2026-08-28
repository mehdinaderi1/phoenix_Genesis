from intelligence.flow import IntelligenceFlow

from intelligence.consensus import ConsensusResult

from intelligence.meta.meta_insight import MetaInsight


class HighReliabilityMetaIntelligence:

    def analyze(
        self,
        decision_records,
        meta_feedback_records=None
    ):

        return MetaInsight(
            samples=10,
            reliability="HIGH"
        )


class LowReliabilityMetaIntelligence:

    def analyze(
        self,
        decision_records,
        meta_feedback_records=None
    ):

        return MetaInsight(
            samples=10,
            reliability="LOW"
        )


def test_meta_learning_increases_confidence_inside_flow():

    flow = IntelligenceFlow()

    flow.meta_intelligence = (
        HighReliabilityMetaIntelligence()
    )

    consensus = ConsensusResult(
        trend="BULLISH",
        signal="BUY",
        confidence=85
    )

    report = flow.create_report(
        consensus
    )

    assert report is not None

    assert report.confidence == 90


def test_meta_learning_reduces_confidence_inside_flow():

    flow = IntelligenceFlow()

    flow.meta_intelligence = (
        LowReliabilityMetaIntelligence()
    )

    consensus = ConsensusResult(
        trend="BULLISH",
        signal="BUY",
        confidence=85
    )

    report = flow.create_report(
        consensus
    )

    assert report is not None

    assert report.confidence == 80
