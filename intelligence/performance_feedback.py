class PerformanceFeedback:


    def evaluate(
        self,
        outcome_or_decision,
        entry_price=None,
        exit_price=None
    ):

        if entry_price is None and exit_price is None:

            outcome = outcome_or_decision

            decision = outcome.decision

            entry_price = outcome.entry_price

            exit_price = outcome.exit_price

        else:

            decision = outcome_or_decision


        if decision.action == "PREPARE_LONG":

            if exit_price > entry_price:

                return {

                    "result": "SUCCESS",

                    "score": 100

                }


            else:

                return {

                    "result": "FAILED",

                    "score": 0

                }



        if decision.action == "PREPARE_SHORT":

            if exit_price < entry_price:

                return {

                    "result": "SUCCESS",

                    "score": 100

                }


            else:

                return {

                    "result": "FAILED",

                    "score": 0

                }



        return {

            "result": "UNKNOWN",

            "score": 50

        }