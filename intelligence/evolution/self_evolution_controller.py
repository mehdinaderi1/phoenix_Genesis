from intelligence.evolution.evolution_governance_bridge import (
        EvolutionGovernanceBridge
)


class SelfEvolutionController:

    
    def __init__(
        self,
        evolution_engine,
        analytics,
        decision,
        rollback,
        history=None,
        recall=None,
        intelligence=None,
        governance_bridge=None
    ):

        self.evolution_engine = evolution_engine
        self.analytics = analytics
        self.decision = decision
        self.rollback = rollback
        self.history = history
        self.recall = recall
        self.intelligence = intelligence

        self.governance_bridge = governance_bridge


    def run(
        self,
        strategy,
        score
    ):

        recall_analysis = None

        intelligence_analysis = None


        if (
            self.intelligence
            and isinstance(strategy, dict)
        ):

            intelligence_analysis = (
                self.intelligence.evaluate(
                    strategy["name"]
                )
            )


            if intelligence_analysis["decision"] != "ALLOW":

                return {

                    "action": "BLOCKED",

                    "reason": (
                        intelligence_analysis["decision"]
                    ),

                    "intelligence": intelligence_analysis

                }



        if (
            self.recall
            and isinstance(strategy, dict)
        ):

            if hasattr(
                self.recall,
                "analyze"
            ):

                recall_analysis = (
                    self.recall.analyze(
                        strategy["name"]
                    )
                )


            elif hasattr(
                self.recall,
                "find_lineage"
            ):

                lineage = (
                    self.recall.find_lineage(
                        strategy["name"]
                    )
                )


                recall_analysis = {

                    "known": bool(lineage),

                    "evolution_count": len(lineage),

                }



        evolved = self.evolution_engine.evolve(
            strategy,
            score
        )


        if not evolved["evolved"]:

            return {

                "action": "NO_EVOLUTION",

                "strategy": strategy,

                "result": evolved,

                "recall": recall_analysis,

                "intelligence": intelligence_analysis,

            }

        governance_result = None


        if self.governance_bridge:

            governance_result = (
                self.governance_bridge.evaluate(
                    evolved["strategy"]
                )
            )


        if (
            governance_result
            and not governance_result["approved"]
        ):


            return {

                "action": "BLOCKED",

                "reason":
                "Evolution rejected by governance",

                "strategy": evolved,

                "governance":
                    governance_result,

                "recall":
                    recall_analysis,

                "intelligence":
                    intelligence_analysis,

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

                "recall": recall_analysis,

                "intelligence": intelligence_analysis,

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

                timestamp=datetime.now(
                    timezone.utc
                )

            )


            self.history.add(
                record
            )



        return {

            "action": decision["decision"],

            "decision": decision,

            "strategy": evolved,

            "recall": recall_analysis,

            "intelligence": intelligence_analysis,

        }