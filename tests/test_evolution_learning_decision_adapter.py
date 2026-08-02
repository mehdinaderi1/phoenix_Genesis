class EvolutionLearningDecisionAdapter:


    def decide(
        self,
        decision,
        learning_context
    ):


        if (
            learning_context
            and learning_context.get(
                "has_history"
            )
        ):


            confidence = (
                learning_context.get(
                    "confidence",
                    0
                )
            )


            if confidence >= 0.9:

                return {

                    "decision":
                        decision["decision"],

                    "reason":
                        "confirmed by previous learning",

                    "learning_applied":
                        True

                }



            if confidence < 0.5:

                return {

                    "decision":
                        "REVIEW",

                    "reason":
                        "low learning confidence",

                    "learning_applied":
                        True

                }



        return {

            "decision":
                decision["decision"],

            "reason":
                decision["reason"],

            "learning_applied":
                False

        }



def test_learning_confidence_confirms_decision():


    adapter = EvolutionLearningDecisionAdapter()


    result = adapter.decide(

        {

            "decision": "KEEP",

            "reason": "performance improved"

        },

        {

            "has_history": True,

            "confidence": 0.95

        }

    )


    assert result["decision"] == "KEEP"


    assert result["learning_applied"] is True


    assert (
        result["reason"]
        ==
        "confirmed by previous learning"
    )



def test_low_learning_confidence_requests_review():


    adapter = EvolutionLearningDecisionAdapter()


    result = adapter.decide(

        {

            "decision": "KEEP",

            "reason": "performance improved"

        },

        {

            "has_history": True,

            "confidence": 0.3

        }

    )


    assert result["decision"] == "REVIEW"


    assert result["learning_applied"] is True



def test_without_learning_keeps_original_decision():


    adapter = EvolutionLearningDecisionAdapter()


    result = adapter.decide(

        {

            "decision": "ROLLBACK",

            "reason": "performance degraded"

        },

        None

    )


    assert result["decision"] == "ROLLBACK"


    assert result["learning_applied"] is False