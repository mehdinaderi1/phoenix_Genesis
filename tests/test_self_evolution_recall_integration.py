from datetime import datetime, timezone


from intelligence.learning.strategy_evolution_engine import (
    StrategyEvolutionEngine,
)


from intelligence.evolution.evolution_history import (
    EvolutionHistory,
    EvolutionRecord,
)


from intelligence.evolution.evolution_recall import (
    EvolutionRecall,
)


from intelligence.evolution.self_evolution_controller import (
    SelfEvolutionController,
)



class DummyAnalytics:
    pass



class DummyDecision:


    def decide(
        self,
        new_score,
        old_score
    ):

        return {
            "decision": "KEEP"
        }



class DummyRollback:
    pass



def test_controller_uses_evolution_recall():


    history = EvolutionHistory()


    history.add(

        EvolutionRecord(

            parent="trend_v1",

            child="trend_v2",

            generation=2,

            reason="previous evolution",

            score_before=80,

            score_after=90,

            timestamp=datetime.now(timezone.utc)

        )

    )


    recall = EvolutionRecall(
        history
    )


    controller = SelfEvolutionController(

        evolution_engine=StrategyEvolutionEngine(),

        analytics=DummyAnalytics(),

        decision=DummyDecision(),

        rollback=DummyRollback(),

        history=history,

        recall=recall

    )


    strategy = {

        "name": "trend_v1",

        "score": 85,

        "success_rate": 0.8

    }


    result = controller.run(

        strategy,

        strategy["score"]

    )


    assert result is not None


    assert controller.recall is recall