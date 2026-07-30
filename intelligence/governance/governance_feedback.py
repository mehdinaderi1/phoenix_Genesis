class GovernanceFeedback:


    def __init__(
        self,
        memory
    ):

        self.memory = memory



    def evaluate(
        self,
        strategy,
        outcome
    ):

        records = self.memory.records


        matched = None


        for record in records:

            if record.strategy == strategy:

                matched = record
                break



        if matched is None:

            return {
                "status": "UNKNOWN",
                "reason": "no governance record"
            }



        if outcome == "SUCCESS":

            feedback = "CONFIRMED"


        elif outcome == "FAILURE":

            feedback = "INCORRECT"


        else:

            feedback = "NEUTRAL"



        return {
            "status": feedback,
            "original_decision": matched.status,
            "strategy": strategy
        }