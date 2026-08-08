class AdaptiveIntelligence:
    """
    Unified intelligence layer for confidence adaptation.

    Combines:
    - Learning reliability
    - Experience performance
    - Strategy history
    """

    def __init__(
        self,
        adaptive_confidence,
        experience_confidence,
        confidence_adjuster
    ):

        self.adaptive_confidence = (
            adaptive_confidence
        )

        self.experience_confidence = (
            experience_confidence
        )

        self.confidence_adjuster = (
            confidence_adjuster
        )


    def adjust_analysis_confidence(
        self,
        base_confidence,
        learning_insight,
        experience_context
    ):

        experience_bonus = (
            self.experience_confidence.calculate(
                experience_context
            )
        )


        return (
            self.adaptive_confidence.adjust(
                base_confidence,
                learning_insight,
                experience_bonus
            )
        )


    def adjust_strategy_confidence(
        self,
        base_confidence,
        strategy
    ):

        experience_bonus = (
            self.experience_confidence.calculate_from_strategy(
                strategy
            )
        )


        return (
            self.confidence_adjuster.adjust(
                base_confidence,
                experience_bonus
            )
        )