class SelfEvolutionController:

    def __init__(
        self,
        evolution_engine,
        analytics,
        decision,
        rollback,
        history=None
    ):

        self.evolution_engine = evolution_engine
        self.analytics = analytics
        self.decision = decision
        self.rollback = rollback
        self.history = history


    def run(
        self,
        strategy,
        score
    ):

        evolved = self.evolution_engine.evolve(
            strategy,
            score
        )


        if not evolved["evolved"]:

            return {
                "action": "NO_EVOLUTION",
                "strategy": strategy,
                "result": evolved,
            }


        parent_score = (
            evolved["score"] - 10
        )


        decision = self.decision.decide(
            evolved["score"],
            parent_score
        )


        if decision["decision"] == "ROLLBACK":

            rollback = self.rollback.rollback(
                evolved["strategy"]
            )

            return {
                "action": "ROLLBACK",
                "decision": decision,
                "rollback": rollback,
            }

        if self.history:


            from datetime import datetime, timezone


            from intelligence.evolution.evolution_history import (
                EvolutionRecord
            )


            record = EvolutionRecord(

                parent=strategy["name"],

                child=evolved["strategy"],

                generation=evolved["generation"],

                reason="self evolution",

                score_before=score,

                score_after=evolved["score"],

                timestamp=datetime.now(timezone.utc)

            )


            self.history.add(
                record
            )


        return {
            "action": decision["decision"],
            "decision": decision,
            "strategy": evolved,
        }