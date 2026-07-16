from intelligence.performance_feedback import PerformanceFeedback



class MockDecision:


    action = "PREPARE_LONG"



def test_performance_feedback():


    feedback = PerformanceFeedback()


    result = feedback.evaluate(

        MockDecision(),

        65000,

        67000

    )


    assert result["result"] == "SUCCESS"


    assert result["score"] == 100