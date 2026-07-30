from intelligence.governance.governance_evolution import (
    GovernanceEvolution
)



def test_governance_evolution_allowed():


    evolution = GovernanceEvolution()


    result = evolution.evaluate(
        {
            "status": "STABLE",
            "confidence": 20
        }
    )


    assert result["decision"] == "ALLOW_EVOLUTION"



def test_governance_evolution_review():


    evolution = GovernanceEvolution()


    result = evolution.evaluate(
        {
            "status": "STABLE",
            "confidence": 0
        }
    )


    assert result["decision"] == "REVIEW"



def test_governance_evolution_blocked():


    evolution = GovernanceEvolution()


    result = evolution.evaluate(
        {
            "status": "REVIEW",
            "confidence": 20
        }
    )


    assert result["decision"] == "BLOCK_EVOLUTION"