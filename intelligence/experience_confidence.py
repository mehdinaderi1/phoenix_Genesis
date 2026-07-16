class ExperienceConfidence:

    def calculate(
        self,
        experience_context
    ):

        total = experience_context.get(
            "total_experiences",
            0
        )

        successful = experience_context.get(
            "successful",
            0
        )

        if total == 0:
            return 0


        success_rate = successful / total


        confidence_bonus = int(
            (success_rate - 0.5) * 20
        )


        return max(
            -10,
            min(
                10,
                confidence_bonus
            )
        )