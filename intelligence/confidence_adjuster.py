class ConfidenceAdjuster:
    """
    Adjusts decision confidence
    using experience based bonus.
    """


    def adjust(
        self,
        base_confidence,
        experience_bonus
    ):

        confidence = (
            base_confidence
            + experience_bonus
        )


        return max(
            0,
            min(
                100,
                confidence
            )
        )