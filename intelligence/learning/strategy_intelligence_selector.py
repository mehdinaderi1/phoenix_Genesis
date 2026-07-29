from dataclasses import dataclass


@dataclass(slots=True)
class IntelligenceSelection:

    strategy: str

    score: float

    reason: str



class StrategyIntelligenceSelector:


    def __init__(
        self,
        knowledge_selector
    ):

        self.knowledge_selector = (
            knowledge_selector
        )


    def select(
        self,
        strategies,
        knowledge_list
    ):

        knowledge_result = (
            self.knowledge_selector.select(
                knowledge_list
            )
        )


        if knowledge_result:

            for strategy in strategies:

                if (
                    strategy.get("name")
                    ==
                    knowledge_result.strategy
                ):

                    return IntelligenceSelection(

                        strategy=knowledge_result.strategy,

                        score=knowledge_result.score,

                        reason=(
                            "Current strategy "
                            "validated by evolution knowledge"
                        )

                    )


        if strategies:

            best = max(

                strategies,

                key=lambda x:
                    x.get(
                        "score",
                        0
                    )

            )


            return IntelligenceSelection(

                strategy=best["name"],

                score=best["score"],

                reason=(
                    "Selected by current performance"
                )

            )


        return None