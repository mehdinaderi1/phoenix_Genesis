class GovernanceAnalyzer:


    def analyze(
        self,
        history
    ):

        if not history:

            return {
                "status": "UNKNOWN",
                "score": 0
            }


        scores = [
            item["confidence"]
            for item in history
        ]


        average = sum(scores) / len(scores)


        if average >= 10:

            status = "STABLE"


        elif average <= 0:

            status = "REVIEW"


        else:

            status = "IMPROVE"



        return {
            "status": status,
            "score": average
        }