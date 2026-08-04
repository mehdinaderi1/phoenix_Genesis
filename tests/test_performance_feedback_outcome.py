from intelligence.performance_feedback import PerformanceFeedback
from intelligence.outcome_record import OutcomeRecord


class MockDecision:

    action = "PREPARE_LONG"



def test_performance_feedback_with_outcome_record():

    outcome = OutcomeRecord(
        decision=MockDecision(),
        entry_price=65000,
        exit_price=67000
    )

    feedback = PerformanceFeedback()

    result = feedback.evaluate(
        outcome
    )

    assert result["result"] == "SUCCESS"

    assert result["score"] == 100