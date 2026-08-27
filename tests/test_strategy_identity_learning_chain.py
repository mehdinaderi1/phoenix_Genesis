from intelligence.experience_record import ExperienceRecord
from intelligence.pattern_intelligence import PatternIntelligence
from intelligence.strategy_memory import StrategyMemory
from intelligence.strategy_learner import StrategyLearner
from intelligence.strategy_recall import StrategyRecall
from intelligence.learning.strategy_ranker import StrategyRanker
from intelligence.strategy_council import StrategyCouncil
from intelligence.strategy_evaluator import StrategyEvaluator



def test_strategy_identity_learning_chain():


    # -------------------------------------------------
    # 1. Champion strategy creates experience history
    # -------------------------------------------------

    experiences = [

        ExperienceRecord(
            "TRENDING_BULLISH",
            "BUY",
            "LOW",
            True,
            85,
            strategy="trend_following",
            champion_strategy="trend_following"
        ),

        ExperienceRecord(
            "TRENDING_BULLISH",
            "BUY",
            "LOW",
            True,
            90,
            strategy="trend_following",
            champion_strategy="trend_following"
        ),

        ExperienceRecord(
            "TRENDING_BULLISH",
            "BUY",
            "LOW",
            True,
            92,
            strategy="trend_following",
            champion_strategy="trend_following"
        ),

        ExperienceRecord(
            "TRENDING_BULLISH",
            "BUY",
            "LOW",
            True,
            87,
            strategy="trend_following",
            champion_strategy="trend_following"
        )

    ]


    # -------------------------------------------------
    # 2. Pattern Intelligence preserves identity
    # -------------------------------------------------

    pattern_intelligence = PatternIntelligence()


    patterns = pattern_intelligence.analyze(
        experiences
    )


    assert patterns

    assert patterns[0]["strategy"] == (
        "trend_following"
    )


    # -------------------------------------------------
    # 3. Learning keeps champion identity
    # -------------------------------------------------

    memory = StrategyMemory()


    learner = StrategyLearner(
        memory,
        evaluator=StrategyEvaluator(
            min_samples=1    
        )
    )


    learned = learner.learn(
        patterns
    )


    assert learned


    assert learned[0]["strategy"] == (
        "trend_following"
    )


    assert memory.count() == 1


    # -------------------------------------------------
    # 4. Recall returns learned strategy
    # -------------------------------------------------

    recall = StrategyRecall(
        memory
    )


    recalled = recall.recall(
        "TRENDING_BULLISH",
        "BUY",
        "LOW"
    )


    assert recalled


    assert recalled[0]["strategy"] == (
        "trend_following"
    )


    # -------------------------------------------------
    # 5. Ranking keeps identity
    # -------------------------------------------------

    ranker = StrategyRanker()


    ranking = ranker.rank(
        recalled
    )


    assert ranking


    top = ranking[0]


    assert top.strategy_name == (
        "trend_following"
    )


    # -------------------------------------------------
    # 6. Council evaluates same strategy
    # -------------------------------------------------

    council = StrategyCouncil()


    result = council.evaluate(
        ranking
    )


    assert result is not None


    assert result.top_strategy == (
        "trend_following"
    )