from intelligence.learning.strategy_version import StrategyVersion
from intelligence.governance.governance_flow import GovernanceFlow



def test_governance_flow_approves_strategy():

    strategy = StrategyVersion(

        name="trend_strategy",

        score=90,

        success_rate=0.85

    )


    flow = GovernanceFlow()


    result = flow.process(strategy)


    assert result["decision"] == "APPROVED"

    assert result["strategy"].status == "CHAMPION"



def test_governance_flow_archives_bad_strategy():

    strategy = StrategyVersion(

        name="weak_strategy",

        score=20,

        success_rate=0.1

    )


    flow = GovernanceFlow()


    result = flow.process(strategy)


    assert result["decision"] == "ARCHIVED"

    assert result["strategy"].status == "ARCHIVED"



def test_governance_flow_review_strategy():

    strategy = StrategyVersion(

        name="average_strategy",

        score=60,

        success_rate=0.5

    )


    flow = GovernanceFlow()


    result = flow.process(strategy)


    assert result["decision"] == "REVIEW"

    assert result["strategy"].status == "REVIEW"