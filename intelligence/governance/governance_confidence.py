class GovernanceConfidence:


    def __init__(
        self
    ):

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


        if self.score < 0:

            self.score = 0


        if self.score > 100:

            self.score = 100


        return self.score