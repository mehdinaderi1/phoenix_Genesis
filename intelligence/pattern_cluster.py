class PatternCluster:


    def cluster(
        self,
        experiences
    ):

        clusters = {}


        for exp in experiences:

            key = (
                f"{exp.regime}_"
                f"{exp.signal}_"
                f"{exp.risk}"
            )


            if key not in clusters:

                clusters[key] = []


            clusters[key].append(
                exp
            )


        return clusters