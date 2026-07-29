from dataclasses import dataclass


@dataclass(slots=True)
class StrategySelection:

    strategy: str

    score: float

    reason: str



class StrategyKnowledgeSelector:


    def select(
        self,
        knowledge_list
    ):

        if not knowledge_list:

            return None


        best = max(

            knowledge_list,

            key=lambda x:
                (
                    x.average_score *
                    x.average_success_rate
                )

        )


        confidence = round(

            best.average_score *
            best.average_success_rate
            / 100,

            2

        )


        return StrategySelection(

            strategy=best.strategy,

            score=confidence,

            reason="Highest historical evolution performance"

        )