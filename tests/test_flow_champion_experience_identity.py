from intelligence.flow import IntelligenceFlow
from intelligence.consensus import ConsensusResult


def test_flow_preserves_champion_strategy_into_experience():

    flow = IntelligenceFlow()


    # -------------------------------------------------
    # 1. Seed an existing strategy
    # -------------------------------------------------

    flow.strategy_memory.store(
        {
            "name": "trend_following",

            "strategy": "trend_following",

            "regime": "TRENDING_BULLISH",

            "signal": "BUY",

            "risk": "LOW",

            "score": 85,

            "success_rate": 0.85,

            "samples": 20,

            "status": "ACTIVE"
        }
    )


    # -------------------------------------------------
    # 2. Market Consensus
    # -------------------------------------------------

    consensus = ConsensusResult(
        trend="BULLISH",
        signal="BUY",
        confidence=85
    )

      

    # -------------------------------------------------
    # 3. Run Intelligence Flow
    # -------------------------------------------------
    selection = flow.strategy_selector.select_with_result(
        "TRENDING_BULLISH",
        "BUY",
        "LOW"
    )

    print("SELECTION:", selection)

    if selection:
        print(
            "RANKING:",
            selection["ranking"]
        )

        print(
            "CONSENSUS:",
            flow.strategy_council.evaluate(
                selection["ranking"]
            )
        )
        
    report = flow.create_report(
        consensus
    )


    # -------------------------------------------------
    # 4. Champion must exist
    # -------------------------------------------------

    champion = getattr(
        report,
        "champion_strategy",
        None
    )

    assert champion is not None

    assert champion["name"] == (
        "trend_following"
    )


    # -------------------------------------------------
    # 5. Experience must preserve identity
    # -------------------------------------------------

    experiences = (
        flow.experience_memory
        .get_experiences()
    )

    assert experiences

    latest_experience = experiences[-1]


    assert latest_experience.strategy == (
        champion["name"]
    )


    # -------------------------------------------------
    # 6. Full Champion object must survive
    # -------------------------------------------------

    assert latest_experience.champion_strategy == (
        champion
    )