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

        return self.paper_runtime.run(
            cycles=cycles,
            symbol=symbol
        )