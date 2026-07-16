from intelligence.pattern_score import PatternScore


class PatternRanker:


    def rank(self, patterns):

        if not patterns:

            return []


        scored = []


        for pattern in patterns:


            if pattern.samples < 10:

                reliability = "LOW"

                factor = 0.7


            elif pattern.samples <= 50:

                reliability = "MEDIUM"

                factor = 0.85


            else:

                reliability = "HIGH"

                factor = 1.0



            score = (
                pattern.average_quality
                *
                factor
            )


            scored.append(

                PatternScore(

                    regime=pattern.regime,

                    action=pattern.action,

                    samples=pattern.samples,

                    average_quality=pattern.average_quality,

                    reliability=reliability,

                    score=score,

                    rank=0

                )

            )


        scored.sort(

            key=lambda x: x.score,

            reverse=True

        )


        for index, item in enumerate(scored):

            item.rank = index + 1



        return scored