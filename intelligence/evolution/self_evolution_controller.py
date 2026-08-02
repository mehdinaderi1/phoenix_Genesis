from intelligence.evolution.evolution_governance_bridge import (
    EvolutionGovernanceBridge
)


class EvolutionEvaluationResult:

    def __init__(
        self,
        blocked,
        reason
    ):
        self.blocked = blocked
        self.reason = reason



class SelfEvolutionController:

    def __init__(
        self,
        evolution_engine=None,
        analytics=None,
        decision=None,
        rollback=None,
        history=None,
        recall=None,
        intelligence=None,
        governance_bridge=None,
        memory=None,
        learning_context=None,
        learning_decision_adapter=None,
        feedback=None,
        confidence=None,
        confidence_adapter=None,
        orchestrator=None,
        rollback_manager=None
    ):

        self.evolution_engine = evolution_engine
        self.analytics = analytics
        self.decision = decision

        self.rollback = (
            rollback_manager
            if rollback_manager is not None
            else rollback
        )

        self.history = history
        self.recall = recall
        self.intelligence = intelligence
        self.governance_bridge = governance_bridge
        self.memory = memory

        self.learning_context = learning_context
        self.learning_decision_adapter = (
            learning_decision_adapter
        )

        self.feedback = feedback
        self.confidence = confidence
        self.confidence_adapter = confidence_adapter
        self.orchestrator = orchestrator

        # resilience state
        self.last_decision = None



    def evaluate_evolution(
        self,
        evolution
    ):
        """
        Detect harmful evolution.
        Block -> Rollback -> Failure Memory -> HOLD
        """

        performance_score = evolution.get(
            "performance_score",
            0
        )

        success_rate = evolution.get(
            "success_rate",
            0
        )

        confidence = evolution.get(
            "confidence",
            0
        )


        bad_evolution = (
            performance_score < 0.5
            or success_rate < 0.5
            or confidence < 60
        )


        if bad_evolution:

            strategy = evolution.get(
                "strategy"
            )


            if self.rollback:

                self.rollback.rollback(
                    strategy,
                    reason="bad_evolution"
                )


            if self.memory:

                if hasattr(
                    self.memory,
                    "save_failure"
                ):

                    self.memory.save_failure(
                        strategy,
                        reason="bad_evolution"
                    )


            self.last_decision = "HOLD"


            return EvolutionEvaluationResult(
                blocked=True,
                reason="bad_evolution_detected"
            )


        self.last_decision = "CONTINUE"


        return EvolutionEvaluationResult(
            blocked=False,
            reason="healthy_evolution"
        )



    def next_action(
        self
    ):

        if self.last_decision:

            return self.last_decision

        return "CONTINUE"



    def run(
        self,
        strategy,
        score
    ):

        recall_analysis = None
        intelligence_analysis = None
        learning_context = None
        feedback_result = None
        orchestration_result = None


        if (
            self.learning_context
            and isinstance(strategy, dict)
        ):

            learning_context = (
                self.learning_context.build(
                    strategy["name"]
                )
            )



        if (
            self.intelligence
            and isinstance(strategy, dict)
        ):

            intelligence_analysis = (
                self.intelligence.evaluate(
                    strategy["name"]
                )
            )


            if (
                intelligence_analysis["decision"]
                not in
                ["ALLOW", "NEW"]
            ):

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


        if self.orchestrator:

            orchestration_result = (
                self.orchestrator.evaluate(
                    strategy["name"]
                )
            )


            if not orchestration_result["allowed"]:

                return {

                    "action": "BLOCKED",

                    "reason":
                        "Evolution rejected by orchestrator",

                    "orchestrator":
                        orchestration_result

                }



        evolved = self.evolution_engine.evolve(
            strategy,
            score
        )


        confidence_result = None


        if (
            self.confidence
            and evolved.get("evolved")
        ):

            confidence_result = (
                self.confidence.calculate(
                    {
                        "name":
                            evolved["strategy"],

                        "score":
                            evolved["score"],

                        "generation":
                            evolved["generation"],

                        "success_rate":
                            strategy.get(
                                "success_rate",
                                0
                            )
                    }
                )
            )


        if not evolved["evolved"]:

            return {

                "action": "NO_EVOLUTION",

                "strategy": strategy,

                "result": evolved,

                "recall": recall_analysis,

                "intelligence": intelligence_analysis,

                "learning_context": learning_context

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


        if self.confidence_adapter:

            decision = (
                self.confidence_adapter.decide(
                    decision,
                    confidence_result
                )
            )


        if self.learning_decision_adapter:

            decision = (
                self.learning_decision_adapter.decide(
                    decision,
                    learning_context
                )
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

                "learning_context": learning_context

            }


        return {

            "action":
                decision["decision"],

            "decision":
                decision,

            "strategy":
                evolved,

            "confidence":
                confidence_result,

            "recall":
                recall_analysis,

            "intelligence":
                intelligence_analysis,

            "learning_context":
                learning_context,

            "feedback":
                feedback_result,

            "orchestrator":
                orchestration_result,

        }