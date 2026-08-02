from intelligence.evolution.confidence_decision_adapter import (
    ConfidenceDecisionAdapter
)



def test_high_confidence_allows_keep():

    adapter = ConfidenceDecisionAdapter()


    decision = {

        "decision": "KEEP",

        "reason":
            "performance improved"

    }


    confidence = {

        "confidence": 90

    }


    result = adapter.decide(

        decision,

        confidence

    )


    assert (
        result["decision"]
        ==
        "KEEP"
    )


    assert (
        result["reason"]
        ==
        "high confidence evolution"
    )



def test_low_confidence_forces_rollback():

    adapter = ConfidenceDecisionAdapter()


    decision = {

        "decision": "KEEP",

        "reason":
            "performance improved"

    }


    confidence = {

        "confidence": 30

    }


    result = adapter.decide(

        decision,

        confidence

    )


    assert (
        result["decision"]
        ==
        "ROLLBACK"
    )


    assert (
        result["reason"]
        ==
        "low evolution confidence"
    )



def test_missing_confidence_keeps_original_decision():

    adapter = ConfidenceDecisionAdapter()


    decision = {

        "decision": "KEEP",

        "reason":
            "performance improved"

    }


    result = adapter.decide(

        decision,

        None

    )


    assert (
        result["decision"]
        ==
        "KEEP"
    )