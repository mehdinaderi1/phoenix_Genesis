from intelligence.action_proposal import ActionProposal


def test_action_proposal():

    proposal = ActionProposal(
        action="PREPARE_LONG",
        status="APPROVED",
        reason="Strong bullish setup",
        confidence=85
    )

    assert proposal.action == "PREPARE_LONG"
    assert proposal.status == "APPROVED"
    assert proposal.confidence == 85