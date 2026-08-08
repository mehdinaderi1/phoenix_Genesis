from intelligence.strategy_consensus_explanation import (
    StrategyConsensusExplanation
)


class StrategyConsensusExplanationBuilder:
    """
    Builds explainable consensus output
    from strategy decision metadata.
    """

    def build(
        self,
        consensus: dict,
        conflict_result=None,
        resolution=None
    ):

        if not consensus:
            return StrategyConsensusExplanation(
                decision=None,
                reasons=[
                    "No consensus data available"
                ]
            )


        decision = consensus.get(
            "decision"
        )


        confidence = consensus.get(
            "confidence",
            0.0
        )


        dominant_strategy = consensus.get(
            "top_strategy"
        )


        reasons = []


        supporting = consensus.get(
            "supporting_strategies",
            0
        )


        opposing = consensus.get(
            "opposing_strategies",
            0
        )


        if supporting > opposing:

            reasons.append(
                "Majority strategies support decision"
            )


        else:

            reasons.append(
                "No strategy majority detected"
            )


        if confidence >= 0.6:

            reasons.append(
                "Consensus confidence above threshold"
            )

        else:

            reasons.append(
                "Consensus confidence below threshold"
            )



        conflict_detected = False


        if conflict_result:

            conflict_detected = (
                conflict_result.conflict
            )


            if conflict_detected:

                reasons.append(
                    "Strategy conflict detected"
                )



        if resolution:

            reasons.append(
                resolution.get(
                    "reason",
                    "Resolution applied"
                )
            )



        return StrategyConsensusExplanation(

            decision=decision,

            dominant_strategy=
                dominant_strategy,

            supporting_strategies=[
                supporting
            ],

            opposing_strategies=[
                opposing
            ],

            reasons=reasons,

            confidence=confidence,

            conflict_detected=
                conflict_detected,

            metadata={
                "resolution":
                    resolution
            }
        )