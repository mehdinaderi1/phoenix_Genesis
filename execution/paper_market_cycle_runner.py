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
            "report": report,
            "price": price,
            "symbol": symbol,
            "signal": getattr(
                consensus,
                "signal",
                None
            )
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

            action_proposal = cycle_input.get(
                "action_proposal"
            )

            report = cycle_input.get(
                "report"
            )

            execution_result = result.get(
                "execution_result"
            )

            position = result.get(
                "position"
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

                    "signal": cycle_input.get(
                        "signal"
                    ),

                    "trend": getattr(
                        report,
                        "trend",
                        None
                    ),

                    "regime": getattr(
                        report,
                        "regime",
                        None
                    ),

                    "confidence": getattr(
                        report,
                        "confidence",
                        None
                    ),

                    "risk": getattr(
                        report,
                        "risk",
                        None
                    ),

                    "proposal_action": getattr(
                        action_proposal,
                        "action",
                        None
                    ),

                    "proposal_status": getattr(
                        action_proposal,
                        "status",
                        None
                    ),

                    "proposal_reason": getattr(
                        action_proposal,
                        "reason",
                        None
                    ),

                    "action": result.get(
                        "action"
                    ),

                    "execution_status": (
                        execution_result.status
                        if execution_result is not None
                        else None
                    ),

                    "realized_pnl": result.get(
                        "realized_pnl",
                        0.0
                    ),

                    "position_side": getattr(
                        position,
                        "side",
                        None
                    ),

                    "entry_price": getattr(
                        position,
                        "entry_price",
                        None
                    ),

                    "quantity": getattr(
                        position,
                        "quantity",
                        None
                    ),

                    "report": report,

                    "position": position
                }
            )

        return records

    def build_serializable_cycle_records(
        self,
        results
    ):
        records = self.build_cycle_records(
            results
        )

        serializable_records = []

        serializable_fields = (
            "cycle",
            "symbol",
            "price",
            "signal",
            "trend",
            "regime",
            "confidence",
            "risk",
            "proposal_action",
            "proposal_status",
            "proposal_reason",
            "action",
            "execution_status",
            "realized_pnl",
            "position_side",
            "entry_price",
            "quantity"
        )

        for record in records:
            serializable_records.append(
                {
                    field: record.get(field)
                    for field in serializable_fields
                }
            )

        return serializable_records