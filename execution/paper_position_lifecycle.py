class PaperPositionLifecycle:

    def __init__(self, session):
        self.session = session

    def process(
        self,
        action_proposal,
        price,
        symbol="BTCUSDT",
        decision=None
    ):
        position = self.session.get_position()
        action = getattr(action_proposal, "action", None)

        if position is None:
            if action in ("BUY", "SELL"):
                result = self.session.process_action(
                    action_proposal=action_proposal,
                    price=price,
                    symbol=symbol,
                    decision=decision
                )

                if result["position"] is not None:
                    return {
                        "action": "OPEN",
                        "execution_result": result["execution_result"],
                        "position": result["position"],
                        "realized_pnl": 0.0
                    }

            return {
                "action": "HOLD",
                "position": None,
                "realized_pnl": 0.0
            }

        if action == "WAIT":
            return {
                "action": "HOLD",
                "position": position,
                "realized_pnl": 0.0
            }

        if action in ("BUY", "SELL") and action != position.side:
            closed = self.session.close_position(
                exit_price=price
            )

            if closed is None:
                return {
                    "action": "HOLD",
                    "position": position,
                    "realized_pnl": 0.0
                }

            return {
                "action": "CLOSE",
                "position": closed["position"],
                "exit_price": closed["exit_price"],
                "realized_pnl": closed["realized_pnl"],
                "trade": closed["trade"],
                "learning_result": closed.get("learning_result")
            }

        return {
            "action": "HOLD",
            "position": position,
            "realized_pnl": 0.0
        }
