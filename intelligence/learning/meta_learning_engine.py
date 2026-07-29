from dataclasses import dataclass


@dataclass(slots=True)
class MetaLearningInsight:

    strategy: str

    confidence: float

    rule: str

    evidence: int



class MetaLearningEngine:


    def analyze(
        self,
        knowledge
    ):

        if knowledge is None:

            return None


        performance = (
            knowledge.average_score *
            knowledge.average_success_rate
        )


        if performance >= 60:

            rule = (
                "Strategy shows strong "
                "historical evolution pattern"
            )

            confidence = 0.8


        else:

            rule = (
                "Strategy requires further improvement"
            )

            confidence = 0.5


        return MetaLearningInsight(

            strategy=knowledge.strategy,

            confidence=confidence,

            rule=rule,

            evidence=knowledge.generations

        )