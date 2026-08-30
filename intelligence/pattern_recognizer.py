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


        strategies = {}


        for exp in experiences:

            strategy = getattr(
                exp,
                "strategy",
                None
            )

            if not strategy:
                continue


            if strategy not in strategies:

                strategies[strategy] = []


            strategies[strategy].append(
                exp
            )


        strategy_insights = {}


        for strategy, items in strategies.items():

            strategy_samples = len(
                items
            )


            strategy_successful = sum(
                1
                for exp in items
                if exp.success
            )


            strategy_success_rate = (
                strategy_successful
                / strategy_samples
            )


            strategy_avg_score = (
                sum(
                    exp.score
                    for exp in items
                )
                / strategy_samples
            )


            strategy_insights[strategy] = {

                "samples":
                    strategy_samples,

                "success_rate":
                    strategy_success_rate,

                "avg_score":
                    strategy_avg_score

            }


        best_strategy = None


        if strategy_insights:

            best_strategy = max(

                strategy_insights,

                key=lambda strategy:
                    (
                        strategy_insights[
                            strategy
                        ]["success_rate"],

                        strategy_insights[
                            strategy
                        ]["avg_score"],

                        strategy_insights[
                            strategy
                        ]["samples"]
                    )

            )


        return {

            "pattern": pattern,

            "strategy": (
                best_strategy
            ),

            "samples": samples,

            "success_rate": success_rate,

            "avg_score": avg_score,

            "strategies": strategy_insights,

            "best_strategy": best_strategy

        }
