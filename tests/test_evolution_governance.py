from datetime import datetime, timezone

from intelligence.evolution.evolution_history import (
    EvolutionRecord
)

from intelligence.evolution.evolution_governance import (
    EvolutionGovernance
)


class MockIntelligence:

    def evaluate(self, record):

        if record.score_after > record.score_before:
            return {
                "decision": "ALLOW"
            }

        return {
            "decision": "BLOCK"
        }


class MockGovernance:

    def evaluate(self, record):

        if record.score_after > record.score_before:
            return {
                "status": "APPROVED"
            }

        return {
            "status": "BLOCKED"
        }



def test_governance_accepts_improved_evolution():

    governance = EvolutionGovernance(
        MockIntelligence(),
        MockGovernance()
    )


    record = EvolutionRecord(
        parent="trend_v1",
        child="trend_v2",
        generation=2,
        reason="performance",
        score_before=72,
        score_after=88,
        timestamp=datetime.now(timezone.utc),
    )


    result = governance.evaluate(
        record
    )


    assert result["status"] == "APPROVED"



def test_governance_rejects_regression():

    governance = EvolutionGovernance(
        MockIntelligence(),
        MockGovernance()
    )


    record = EvolutionRecord(
        parent="trend_v1",
        child="trend_v2",
        generation=2,
        reason="regression",
        score_before=90,
        score_after=80,
        timestamp=datetime.now(timezone.utc),
    )


    result = governance.evaluate(
        record
    )


    assert result["status"] == "BLOCKED"