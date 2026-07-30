from intelligence.governance.governance_service import (
    GovernanceService
)


class FakeHistory:


    def get_all(
        self
    ):

        return [
            {
                "strategy": "strategy_alpha",
                "confidence": 10
            },
            {
                "strategy": "strategy_alpha",
                "confidence": 20
            }
        ]



def test_governance_service_evaluate():


    service = GovernanceService(
        FakeHistory()
    )


    result = service.evaluate(
        "strategy_alpha"
    )


    assert result["status"] == "STABLE"

    assert result["confidence"] == 15