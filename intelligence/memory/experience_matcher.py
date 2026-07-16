class ExperienceMatch:

    def __init__(
        self,
        similar_cases,
        success_rate,
        average_score
    ):

        self.similar_cases = similar_cases
        self.success_rate = success_rate
        self.average_score = average_score


class ExperienceMatcher:


    def match(
        self,
        current_context,
        experiences
    ):

        similar = []


        for experience in experiences:

            score = 0


            if experience.regime == current_context.regime:

                score += 1


            if experience.signal == current_context.signal:

                score += 1


            if experience.risk == current_context.risk:

                score += 1


            if score >= 2:

                similar.append(experience)



        if not similar:

            return ExperienceMatch(
                similar_cases=0,
                success_rate=0,
                average_score=0
            )



        successes = [
            e for e in similar
            if e.success
        ]


        success_rate = (
            len(successes) /
            len(similar)
        )


        average_score = sum(
            e.score for e in similar
        ) / len(similar)



        return ExperienceMatch(

            similar_cases=len(similar),

            success_rate=success_rate,

            average_score=average_score

        )