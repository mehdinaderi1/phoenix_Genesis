class PatternRecognizer:


    def recognize(
        self,
        experiences
    ):

        if not experiences:

            return None


        first = experiences[0]


        pattern = (
            f"{first.regime}_"
            f"{first.signal}_"
            f"{first.risk}"
        )


        samples = len(experiences)


        successful = sum(
            1
            for exp in experiences
            if exp.success
        )


        success_rate = (
            successful / samples
        )


        avg_score = sum(
            exp.score
            for exp in experiences
        ) / samples


        return {

            "pattern": pattern,

            "samples": samples,

            "success_rate": success_rate,

            "avg_score": avg_score

        }