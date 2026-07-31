from datetime import datetime, timezone

from intelligence.evolution.evolution_history import (
    EvolutionHistory,
    EvolutionRecord,
)


class StrategyEvolutionEngine:

    def __init__(
        self,
        history=None
    ):
        self.history = history or EvolutionHistory()


    def evaluate(
        self,
        strategy
    ):

        if isinstance(strategy, dict):

            score = strategy.get(
                "score",
                0
            )

            success_rate = strategy.get(
                "success_rate",
                0
            )

        else:
            score = 0
            success_rate = 0


        if (
            score >= 80
            and success_rate >= 0.7
        ):

            decision = "KEEP"


        elif (
            score < 50
            or success_rate < 0.3
        ):

            decision = "RETIRE"


        else:

            decision = "IMPROVE"


        return {

            "decision": decision,
            "score": score,
            "success_rate": success_rate

        }


    def evolve(
        self,
        strategy,
        score
    ):


        if isinstance(strategy, dict):

            name = strategy.get(
                "name",
                "strategy"
            )

            generation = strategy.get(
                "generation",
                1
            )

        else:

            name = strategy
            generation = 1


        if score < 70:

            return {

                "strategy": strategy,
                "parent": None,
                "score": score,
                "generation": generation,
                "evolved": False

            }


        child = name + "_v2"


        result = {

            "strategy": child,

            "parent": name,

            "score": score + 10,

            "generation": generation + 1,

            "evolved": True

        }


        self.history.add(

            EvolutionRecord(

                parent=name,

                child=child,

                generation=result["generation"],

                reason="performance",

                score_before=score,

                score_after=result["score"],

                timestamp=datetime.now(
                    timezone.utc
                )

            )

        )


        return result