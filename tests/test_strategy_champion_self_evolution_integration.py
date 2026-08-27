from datetime import datetime, timezone
from intelligence.strategy_memory import StrategyMemory
from intelligence.strategy_recall import StrategyRecall
from intelligence.learning.strategy_ranker import StrategyRanker
from intelligence.strategy_selector import StrategySelector

from intelligence.evolution.evolution_history import (
    EvolutionHistory,
    EvolutionRecord,
)

from intelligence.evolution.evolution_recall import (
    EvolutionRecall,
)

from intelligence.evolution.evolution_recall_analyzer import (
    EvolutionRecallAnalyzer,
)

from intelligence.evolution.evolution_intelligence import (
    EvolutionIntelligence,
)

from intelligence.evolution.self_evolution_controller import (
    SelfEvolutionController,
)

from intelligence.learning.strategy_evolution_engine import (
    StrategyEvolutionEngine,
)

from intelligence.evolution.evolution_analytics import (
    EvolutionAnalytics,
)

from intelligence.evolution.evolution_decision import (
    EvolutionDecision,
)

from intelligence.evolution.rollback_engine import (
    RollbackEngine,
)


def test_strategy_champion_enters_self_evolution_loop():

    # -------------------------------------------------
    # 1. Strategy Memory
    # -------------------------------------------------

    strategy_memory = StrategyMemory()

    strategy_memory.store(
        {
            "name": "trend_following",
            "strategy": "trend_following",
            "regime": "bullish",
            "signal": "BUY",
            "risk": "LOW",
            "score": 85,
            "success_rate": 0.85,
            "samples": 20,
            "status": "ACTIVE",
        }
    )


    # -------------------------------------------------
    # 2. Strategy Selection
    # -------------------------------------------------

    selector = StrategySelector(
        StrategyRecall(strategy_memory),
        StrategyRanker(),
    )


    selection = selector.select_with_result(
        "bullish",
        "BUY",
        "LOW",
    )


    assert selection is not None


    champion = selection["champion"]


    assert champion is not None


    assert champion["strategy"] == (
        "trend_following"
    )


    # -------------------------------------------------
    # 3. Evolution History
    #
    # Existing successful evolution means
    # EvolutionIntelligence will ALLOW evolution.
    # -------------------------------------------------

    evolution_history = EvolutionHistory()


    evolution_history.add(
        EvolutionRecord(
            parent="trend_following",
            child="trend_following_previous_v2",
            generation=2,
            reason="previous successful evolution",
            score_before=75,
            score_after=85,
            timestamp=datetime.now(timezone.utc),
        )
    )


    # -------------------------------------------------
    # 4. Evolution Intelligence
    # -------------------------------------------------

    evolution_recall = EvolutionRecall(
        evolution_history
    )


    evolution_analyzer = EvolutionRecallAnalyzer(
        evolution_recall
    )


    evolution_intelligence = EvolutionIntelligence(
        evolution_analyzer
    )


    permission = evolution_intelligence.evaluate(
        champion["name"]
    )


    assert permission["decision"] == "ALLOW"


    # -------------------------------------------------
    # 5. Self Evolution Controller
    # -------------------------------------------------

    evolution_engine = StrategyEvolutionEngine(
        history=evolution_history
    )


    controller = SelfEvolutionController(

        evolution_engine=evolution_engine,

        analytics=EvolutionAnalytics(
            evolution_history
        ),

        decision=EvolutionDecision(),

        rollback=RollbackEngine(
            evolution_history
        ),

        history=evolution_history,

        recall=evolution_recall,

        intelligence=evolution_intelligence,
    )


    # -------------------------------------------------
    # 6. Champion enters evolution
    # -------------------------------------------------

    result = controller.run(
        champion,
        champion["score"],
    )


    assert result is not None


    assert result["action"] == "KEEP"


    assert result["strategy"]["strategy"] == (
        "trend_following_v2"
    )


    assert result["strategy"]["parent"] == (
        "trend_following"
    )


    assert result["strategy"]["evolved"] is True


    # -------------------------------------------------
    # 7. Evolution History proves the loop completed
    # -------------------------------------------------

    lineage = evolution_recall.find_lineage(
        "trend_following"
    )


    assert lineage


    latest = lineage[-1]


    assert latest.parent == (
        "trend_following"
    )


    assert latest.child == (
        "trend_following_v2"
    )


    assert latest.score_after > (
        latest.score_before
    )