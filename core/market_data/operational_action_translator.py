class OperationalActionTranslator:
    """Translate intelligence actions into paper execution actions."""

    _ACTION_MAP = {
        "PREPARE_LONG": "BUY",
        "PREPARE_SHORT": "SELL",
        "WAIT": "WAIT",
    }

    def translate(self, action_proposal):
        if action_proposal is None:
            raise ValueError("action_proposal must not be None")

        action = getattr(action_proposal, "action", None)

        if action not in self._ACTION_MAP:
            return action_proposal

        translated_action = self._ACTION_MAP[action]

        if translated_action == action:
            return action_proposal

        from intelligence.action_proposal import ActionProposal

        return ActionProposal(
            action=translated_action,
            status=action_proposal.status,
            reason=action_proposal.reason,
            confidence=action_proposal.confidence,
            symbol=action_proposal.symbol,
            strategy=action_proposal.strategy,
            risk_status=action_proposal.risk_status,
            metadata={
                **action_proposal.metadata,
                "translated_from": action,
            },
        )
