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