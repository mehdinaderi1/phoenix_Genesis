from dataclasses import dataclass


@dataclass
class StrategyConfidenceInfluence:

    confidence: float

    adjustment: float

    reason: str



class StrategyConfidenceInfluencer:


    def influence(
        self,
        current_confidence,
        strategy_intelligence
    ):

        if strategy_intelligence is None:

            return StrategyConfidenceInfluence(

                confidence=current_confidence,

                adjustment=0.0,

                reason="No strategy intelligence"

            )


        if not strategy_intelligence.has_evolution_knowledge:

            return StrategyConfidenceInfluence(

                confidence=current_confidence,

                adjustment=0.0,

                reason="No evolution knowledge"

            )


        learning_confidence = (
            strategy_intelligence.learning_confidence
        )


        if learning_confidence >= 0.8:

            adjustment = 0.10

            reason = (
                "Strong strategy evolution confidence"
            )


        elif learning_confidence >= 0.5:

            adjustment = 0.05

            reason = (
                "Moderate strategy evolution confidence"
            )


        else:

            adjustment = 0.0

            reason = (
                "Weak strategy evolution confidence"
            )


        new_confidence = min(

            current_confidence + adjustment,

            1.0

        )


        return StrategyConfidenceInfluence(

            confidence=new_confidence,

            adjustment=adjustment,

            reason=reason

        )