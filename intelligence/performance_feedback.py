class PerformanceFeedback:


    def evaluate(
        self,
        decision,
        entry_price,
        exit_price
    ):


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