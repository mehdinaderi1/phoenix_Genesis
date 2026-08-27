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


        strategy = None


        for exp in experiences:

            champion_strategy = getattr(
                exp,
                "champion_strategy",
                None
            )

            if champion_strategy:

                if isinstance(
                    champion_strategy,
                    dict
                ):

                    strategy = champion_strategy.get(
                        "name"
                    )

                else:

                    strategy = champion_strategy

                break

        strategies = [
            exp.strategy
            for exp in experiences
            if exp.strategy
        ]

        champion_strategy = None

        if strategies:
            champion_strategy = max(
                set(strategies),
                key=strategies.count
            )

        return {

            "pattern": pattern,

            "strategy": strategy,

            "samples": samples,

            "success_rate": success_rate,

            "avg_score": avg_score

        }