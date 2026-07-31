class SelfEvolutionController:

    def __init__(
        self,
        evolution_engine,
        analytics,
        decision,
        rollback,
    ):

        self.evolution_engine = evolution_engine
        self.analytics = analytics
        self.decision = decision
        self.rollback = rollback


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


        return {
            "action": decision["decision"],
            "decision": decision,
            "strategy": evolved,
        }