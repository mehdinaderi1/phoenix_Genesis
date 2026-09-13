from execution.paper_trading_runtime import PaperTradingRuntime
from execution.paper_session_serializer import (
    PaperSessionSerializer
)
from execution.paper_session_archive import (
    PaperSessionArchive
)


class PaperMarketCycleRunner:

    def __init__(
        self,
        exchange_manager,
        multi_timeframe_pipeline,
        intelligence_flow,
        session,
        session_archive=None,
        market_data_pipeline=None
    ):
        self.exchange_manager = exchange_manager
        self.multi_timeframe_pipeline = (
            multi_timeframe_pipeline
        )
        self.intelligence_flow = intelligence_flow

        self.intelligence_flow.enable_inline_outcome_learning = False

        self.session = session

        if getattr(self.session, "outcome_bridge", None) is None:
            self.session.outcome_bridge = getattr(
                intelligence_flow,
                "decision_outcome_bridge",
                None
            )

        self.paper_runtime = PaperTradingRuntime(
            session=self.session
        )

        self.session_archive = session_archive
        self.market_data_pipeline = market_data_pipeline

        self.last_cycle_inputs = []

    def refresh_market_data(
        self,
        symbol="BTCUSDT"
    ):
        if self.market_data_pipeline is None:
            return None

        return self.market_data_pipeline.fetch_multi_timeframes(
            symbol=symbol
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
            "report": report,
            "price": price,
            "symbol": symbol,
            "signal": getattr(
                consensus,
                "signal",
                None
            ),
            "decision": getattr(
                report,
                "decision",
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
            self.refresh_market_data(
                symbol=symbol
            )

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

    def build_session_record(
        self,
        results
    ):
        summary = self.build_summary(
            results
        )

        return {
            "session_id": self.session.session_id,
            "cycles": (
                self.build_serializable_cycle_records(
                    results
                )
            ),
            "summary": summary,
            "final_position": summary.get(
                "current_position"
            )
        }

    def serialize_session(
        self,
        results
    ):
        session_record = self.build_session_record(
            results
        )

        serializer = PaperSessionSerializer()

        return serializer.serialize(
            session_record
        )

    def save_session(
        self,
        results
    ):
        if self.session_archive is None:
            raise ValueError(
                "session_archive is required"
            )

        session_record = self.build_session_record(
            results
        )

        self.session_archive.save(
            self.session.session_id,
            session_record
        )

        return session_record
