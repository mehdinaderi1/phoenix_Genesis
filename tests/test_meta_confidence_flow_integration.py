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

def test_meta_adjusted_confidence_is_consistent_across_final_outputs():

    flow = IntelligenceFlow()

    flow.meta_intelligence = (
        HighReliabilityMetaIntelligence()
    )

    consensus = ConsensusResult(
        trend="BULLISH",
        signal="BUY",
        confidence=85
    )

    report = flow.create_report(consensus)

    assert report is not None

    decision = report.decision
    proposal = report.action_proposal

    # Meta-adjusted confidence must be reflected consistently.
    assert report.confidence == 90
    assert decision.confidence == report.confidence
    assert proposal.confidence == report.confidence

    # The final decision trace must use the adjusted confidence.
    assert decision.trace["confidence"] == report.confidence
