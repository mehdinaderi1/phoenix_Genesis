from execution.paper_position_lifecycle import PaperPositionLifecycle


class PaperTradingCycle:

    def __init__(self, session, lifecycle=None):
        self.session = session

        self.lifecycle = (
            lifecycle
            or PaperPositionLifecycle(session)
        )

    def process(
        self,
        action_proposal,
        price,
        symbol="BTCUSDT"
    ):
        result = self.lifecycle.process(
            action_proposal=action_proposal,
            price=price,
            symbol=symbol
        )

        return {
            "action": result["action"],
            "execution_result": result.get(
                "execution_result"
            ),
            "position": result.get(
                "position"
            ),
            "exit_price": result.get(
                "exit_price"
            ),
            "realized_pnl": result.get(
                "realized_pnl",
                0.0
            ),
            "trade": result.get(
                "trade"
            )
        }