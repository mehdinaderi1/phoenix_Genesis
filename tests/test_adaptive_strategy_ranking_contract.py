from intelligence.memory.experience_memory import ExperienceMemory
from intelligence.pattern_intelligence import PatternIntelligence
from intelligence.strategy_learner import StrategyLearner
from intelligence.strategy_memory import StrategyMemory
from intelligence.strategy_recall import StrategyRecall
from intelligence.strategy_ranker import StrategyRanker


def make_experience(
    strategy,
    success,
    score
):

    from intelligence.experience_record import ExperienceRecord

    return ExperienceRecord(
        regime="TREND",
        signal="BUY",
        risk="LOW",
        success=success,
        score=score,
        decision="BUY",
        strategy=strategy,
        confidence=80,
        trace={},
        champion_strategy=None
    )


def test_adaptive_strategy_ranking_preserves_multi_strategy_performance():

    experience_memory = ExperienceMemory()

    for _ in range(8):

        experience_memory.save_experience(
            make_experience(
                "strategy_A",
                True,
                80
            )
        )

    for _ in range(2):

        experience_memory.save_experience(
            make_experience(
                "strategy_A",
                False,
                40
            )
        )

    for _ in range(7):

        experience_memory.save_experience(
            make_experience(
                "strategy_B",
                True,
                70
            )
        )

    for _ in range(3):

        experience_memory.save_experience(
            make_experience(
                "strategy_B",
                False,
                40
            )
        )


    pattern_intelligence = PatternIntelligence()

    patterns = pattern_intelligence.analyze(
        experience_memory.get_experiences()
    )


    strategy_memory = StrategyMemory()

    learner = StrategyLearner(
        strategy_memory=strategy_memory
    )

    learned = learner.learn(
        patterns
    )


    assert len(learned) == 2

    assert {
        item["strategy"]
        for item in learned
    } == {
        "strategy_A",
        "strategy_B"
    }


    recall = StrategyRecall(
        strategy_memory
    )

    strategies = recall.recall(
        "TREND",
        "BUY",
        "LOW"
    )


    assert len(strategies) == 2

    assert {
        item["strategy"]
        for item in strategies
    } == {
        "strategy_A",
        "strategy_B"
    }


    ranker = StrategyRanker()

    result = ranker.rank_with_result(
        strategies
    )


    assert result.top_strategy is not None

    assert (
        result.top_strategy.strategy_name
        == "strategy_A"
    )


    ranked_names = [
        item.strategy_name
        for item in result.ranked_strategies
    ]


    assert ranked_names == [
        "strategy_A",
        "strategy_B"
    ]


    assert len(
        result.ranked_strategies
    ) == 2


    for item in result.ranked_strategies:

        assert item.strategy_name in {
            "strategy_A",
            "strategy_B"
        }

        assert item.strategy_record["strategy"] == (
            item.strategy_name
        )

        assert "score" in (
            item.score_breakdown
        )

        assert "success_rate" in (
            item.score_breakdown
        )

        assert "samples" in (
            item.score_breakdown
        )
