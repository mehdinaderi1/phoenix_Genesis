from execution.paper_trading_runtime import PaperTradingRuntime


class PaperMarketCycleRunner:

    def __init__(
        self,
        exchange_manager,
        multi_timeframe_pipeline,
        intelligence_flow,
        session
    ):
        self.exchange_manager = exchange_manager
        self.multi_timeframe_pipeline = (
            multi_timeframe_pipeline
        )
        self.intelligence_flow = intelligence_flow

        self.paper_runtime = PaperTradingRuntime(
            session=session
        )

        self.last_cycle_inputs = []

    def build_cycle_input(
        self,
        symbol="BTCUSDT"
    ):
        price = self.exchange_manager.get_price(
            symbol
        )

        consensus = (
            self.multi_timeframe_pipeline.analyze(
                symbol
            )
        )

        report = (
            self.intelligence_flow.create_report(
                consensus
            )
        )

        return {
            "action_proposal": report.action_proposal,
            "price": price,
            "symbol": symbol
        }

    def run(
        self,
        cycle_count=1,
        symbol="BTCUSDT"
    ):
        cycles = []

        for _ in range(cycle_count):
            cycles.append(
                self.build_cycle_input(
                    symbol=symbol
                )
            )

        self.last_cycle_inputs = list(cycles)

        return self.paper_runtime.run(
            cycles=cycles,
            symbol=symbol
        )

    def build_summary(
        self,
        results
    ):
        return self.paper_runtime.build_summary(
            results
        )

    def build_cycle_records(
        self,
        results
    ):
        records = []

        for index, result in enumerate(
            results,
            start=1
        ):
            cycle_input = (
                self.last_cycle_inputs[index - 1]
                if index - 1 < len(
                    self.last_cycle_inputs
                )
                else {}
            )

            records.append(
                {
                    "cycle": index,
                    "symbol": cycle_input.get(
                        "symbol"
                    ),
                    "price": cycle_input.get(
                        "price"
                    ),
                    "action": result.get(
                        "action"
                    ),
                    "realized_pnl": result.get(
                        "realized_pnl",
                        0.0
                    ),
                    "position": result.get(
                        "position"
                    )
                }
            )

        return records