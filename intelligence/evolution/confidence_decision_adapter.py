class ConfidenceDecisionAdapter:


    def decide(
        self,
        decision,
        confidence
    ):

        if not confidence:

            return decision


        score = confidence.get(
            "confidence",
            0
        )


        if score < 50:

            return {

                "decision": "ROLLBACK",

                "reason":
                    "low evolution confidence"

            }


        if (
            score >= 80
            and decision["decision"] == "KEEP"
        ):

            return {

                "decision": "KEEP",

                "reason":
                    "high confidence evolution"

            }


        return decision