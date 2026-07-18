class StrategyPerformanceAnalyzer:


    def analyze(
        self,
        history
    ):

        if not history:

            return {
                "samples": 0,
                "success_rate": 0,
                "average_score": 0
            }


        samples = len(history)


        successes = sum(
            1
            for item in history
            if item.get("success", False)
        )


        success_rate = successes / samples


        average_score = (
            sum(
                item.get("score", 0)
                for item in history
            )
            / samples
        )


        return {

            "samples": samples,

            "success_rate": success_rate,

            "average_score": average_score

        }