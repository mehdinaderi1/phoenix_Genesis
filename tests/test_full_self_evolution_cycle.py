from intelligence.evolution.evolution_history import (
    EvolutionHistory
)

from intelligence.evolution.evolution_recall import (
    EvolutionRecall
)

from intelligence.evolution.evolution_recall_analyzer import (
    EvolutionRecallAnalyzer
)

from intelligence.evolution.evolution_intelligence import (
    EvolutionIntelligence
)

from intelligence.evolution.self_evolution_controller import (
    SelfEvolutionController
)

from intelligence.learning.strategy_evolution_engine import (
    StrategyEvolutionEngine
)

from intelligence.evolution.evolution_analytics import (
    EvolutionAnalytics
)

from intelligence.evolution.evolution_decision import (
    EvolutionDecision
)

from intelligence.evolution.rollback_engine import (
    RollbackEngine
)


def test_full_self_evolution_cycle():

    history = EvolutionHistory()


    recall = EvolutionRecall(
        history
    )


    recall_analyzer = EvolutionRecallAnalyzer(
        recall
    )


    intelligence = EvolutionIntelligence(
        recall_analyzer
    )


    controller = SelfEvolutionController(

        evolution_engine=StrategyEvolutionEngine(
            history=history
        ),

        analytics=EvolutionAnalytics(
            history
        ),

        decision=EvolutionDecision(),

        rollback=RollbackEngine(
            history
        ),

        history=history,

        recall=recall,

        intelligence=intelligence
    )


    strategy = {

        "name": "scalp_alpha_v1",

        "score": 85

    }


    result = controller.run(
        strategy,
        85
    )


    assert result is not None


    assert (
        "action"
        in result
    )


    lineage = recall.find_lineage(
        "scalp_alpha_v1"
    )


    assert lineage is not None