from intelligence.flow import IntelligenceFlow
from intelligence.consensus import ConsensusResult


def test_experience_saved_after_report():

    flow = IntelligenceFlow()


    consensus = ConsensusResult(
        trend="BULLISH",
        signal="BUY",
        confidence=80
    )


    report = flow.create_report(
        consensus
    )


    assert len(
        flow.experience_memory.experiences
    ) == 1