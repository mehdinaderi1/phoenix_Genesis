class StrategyConfidence:


    def calculate(
        self,
        strategy_record
    ):

        score = strategy_record.get(
            "score",
            0
        )

        success_rate = strategy_record.get(
            "success_rate",
            0
        )

        samples = strategy_record.get(
            "samples",
            0
        )


        confidence = (
            score * 0.5
            +
            success_rate * 100 * 0.4
            +
            min(samples, 100) * 0.1
        )


        return round(
            min(confidence, 100),
            2
        )