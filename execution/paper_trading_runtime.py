from execution.paper_trading_cycle import PaperTradingCycle


class PaperTradingRuntime:

    def __init__(
        self,
        session,
        cycle=None
    ):
        self.session = session

        self.cycle = (
            cycle
            or PaperTradingCycle(session)
        )

    def run(
        self,
        cycles,
        symbol="BTCUSDT"
    ):
        results = []

        for cycle_input in cycles:

            result = self.cycle.process(
                action_proposal=cycle_input[
                    "action_proposal"
                ],
                price=cycle_input["price"],
                symbol=cycle_input.get(
                    "symbol",
                    symbol
                )
            )

            results.append(result)

        return results

    def build_summary(
        self,
        results
    ):
        open_count = sum(
            result["action"] == "OPEN"
            for result in results
        )

        close_count = sum(
            result["action"] == "CLOSE"
            for result in results
        )

        hold_count = sum(
            result["action"] == "HOLD"
            for result in results
        )

        position = self.session.get_position()

        return {
            "cycles_processed": len(results),
            "open_count": open_count,
            "close_count": close_count,
            "hold_count": hold_count,
            "current_position": position,
            "balance": self.session.get_balance(),
            "total_pnl": self.session.get_total_pnl(),
            "trade_count": self.session.get_trade_count()
        }