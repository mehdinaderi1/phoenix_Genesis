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

        score = strategy.get(
            "score",
            0
        )

        success_rate = strategy.get(
            "success_rate",
            0
        )


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

        if score < 70:

            return {
                "strategy": strategy,
                "parent": None,
                "score": score,
                "generation": 1,
                "evolved": False
            }


        result = {

            "strategy": strategy["name"] + "_v2",

            "parent": strategy["name"],

            "score": score + 10,

            "generation": strategy.get(
                "generation",
                1
            ) + 1,

            "evolved": True

        }

        self.history.add(
            EvolutionRecord(
                parent=strategy,
                child=result["strategy"],
                generation=result["generation"],
                reason="performance",
                score_before=score,
                score_after=result["score"],
                timestamp=datetime.now(timezone.utc),
            )
        )


        return result