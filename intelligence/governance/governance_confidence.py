class GovernanceConfidence:


    def __init__(self):

        self.score = 0



    def calculate(
        self,
        feedback
    ):

        status = feedback.get(
            "status"
        )


        if status == "CONFIRMED":

            self.score += 10


        elif status == "INCORRECT":

            self.score -= 10


        return self.score



    def value(self):

        return self.score