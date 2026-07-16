class AdaptiveConfidence:


    def adjust(
        self,
        base_confidence,
        learning_insight,
        experience_bonus=0
    ):

        adjustment = 0


        if learning_insight.reliability == "HIGH":

            adjustment += 10


        elif learning_insight.reliability == "LOW":

            adjustment -= 10


        elif learning_insight.reliability == "MEDIUM":

            adjustment += 5



        adjustment += experience_bonus



        confidence = base_confidence + adjustment


        if confidence > 100:

            confidence = 100


        if confidence < 0:

            confidence = 0


        return confidence