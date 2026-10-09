from pathlib import Path
from datetime import datetime, timezone
import json

from execution.paper_trading_runtime import PaperTradingRuntime
from execution.paper_trading_session import PaperTradingSession
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

    def refresh_market_data(self, symbol="BTCUSDT"):
        if self.market_data_pipeline is None:
            return None
        return self.market_data_pipeline.fetch_multi_timeframes(
            symbol=symbol
        )

    def build_cycle_input(self, symbol="BTCUSDT"):
        price = self.exchange_manager.get_price(symbol)
        consensus = self.multi_timeframe_pipeline.analyze(symbol)
        report = self.intelligence_flow.create_report(consensus)
        return {
            "action_proposal": report.action_proposal,
            "report": report,
            "price": price,
            "symbol": symbol,
            "signal": getattr(consensus, "signal", None),
            "decision": getattr(report, "decision", None)
        }

    def run(self, cycle_count=1, symbol="BTCUSDT"):
        cycles = []
        results = []
        completed_cycles = getattr(
            self,
            "last_completed_cycle",
            0
        )

        self.last_cycle_inputs = []

        for _ in range(cycle_count):
            self.refresh_market_data(symbol=symbol)
            cycle_input = self.build_cycle_input(
                symbol=symbol
            )

            self.last_cycle_inputs.append(cycle_input)

            cycle_results = self.paper_runtime.run(
                cycles=[cycle_input],
                symbol=symbol
            )

            if len(cycle_results) != 1:
                raise RuntimeError(
                    "Expected exactly one result for each cycle"
                )

            results.extend(cycle_results)
            completed_cycles += 1
            self.last_completed_cycle = completed_cycles

            if self.session_archive is not None:
                checkpoint = self.build_runtime_checkpoint(
                    completed_cycles=completed_cycles,
                    symbol=symbol
                )
                self.save_runtime_checkpoint(checkpoint)

        return results
    def build_summary(self, results):
        return self.paper_runtime.build_summary(results)

    def build_cycle_records(self, results):
        records = []
        for index, result in enumerate(results, start=1):
            cycle_input = (
                self.last_cycle_inputs[index - 1]
                if index - 1 < len(self.last_cycle_inputs)
                else {}
            )
            action_proposal = cycle_input.get("action_proposal")
            report = cycle_input.get("report")
            execution_result = result.get("execution_result")
            position = result.get("position")

            records.append({
                "cycle": index,
                "symbol": cycle_input.get("symbol"),
                "price": cycle_input.get("price"),
                "signal": cycle_input.get("signal"),
                "trend": getattr(report, "trend", None),
                "regime": getattr(report, "regime", None),
                "confidence": getattr(report, "confidence", None),
                "risk": getattr(report, "risk", None),
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
                "action": result.get("action"),
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
            })

        return records

    def build_serializable_cycle_records(self, results):
        records = self.build_cycle_records(results)
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
            serializable_records.append({
                field: record.get(field)
                for field in serializable_fields
            })

        return serializable_records

    def build_session_record(self, results):
        summary = self.build_summary(results)

        return {
            "session_id": self.session.session_id,
            "cycles": self.build_serializable_cycle_records(
                results
            ),
            "summary": summary,
            "final_position": summary.get(
                "current_position"
            )
        }

    def build_runtime_checkpoint(
        self,
        completed_cycles,
        symbol="BTCUSDT"
    ):
        return {
            "session_id": self.session.session_id,
            "last_completed_cycle": completed_cycles,
            "symbol": symbol,
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
            "session": self.session.build_checkpoint()
        }

    def save_runtime_checkpoint(self, checkpoint):
        if self.session_archive is None:
            raise ValueError(
                "session_archive is required"
            )

        path = (
            self.session_archive.root_path
            / f"{self.session.session_id}.checkpoint.json"
        )

        path.write_text(
            json.dumps(checkpoint),
            encoding="utf-8"
        )

        self.last_completed_cycle = int(
            checkpoint.get("last_completed_cycle", 0)
        )
        return checkpoint

    def load_runtime_checkpoint(self, session_id=None):
        if self.session_archive is None:
            raise ValueError(
                "session_archive is required"
            )

        root_path = self.session_archive.root_path

        if session_id is not None:
            path = (
                root_path
                / f"{session_id}.checkpoint.json"
            )
            return json.loads(
                path.read_text(
                    encoding="utf-8"
                )
            )

        current_path = (
            root_path
            / f"{self.session.session_id}.checkpoint.json"
        )

        if current_path.exists():
            return json.loads(
                current_path.read_text(
                    encoding="utf-8"
                )
            )

        checkpoint_paths = sorted(
            root_path.glob("*.checkpoint.json")
        )

        if len(checkpoint_paths) == 0:
            raise FileNotFoundError(
                "No runtime checkpoint found"
            )

        if len(checkpoint_paths) > 1:
            raise RuntimeError(
                "Multiple runtime checkpoints found; "
                "session_id is required"
            )

        return json.loads(
            checkpoint_paths[0].read_text(
                encoding="utf-8"
            )
        )
    def serialize_session(self, results):
        session_record = self.build_session_record(
            results
        )
        serializer = PaperSessionSerializer()
        return serializer.serialize(
            session_record
        )

    def save_session(self, results):
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
    def restore_runtime_checkpoint(self):
        checkpoint = self.load_runtime_checkpoint()

        self.session = PaperTradingSession.from_checkpoint(
            checkpoint["session"]
        )

        self.paper_runtime = PaperTradingRuntime(
            session=self.session
        )

        if getattr(self.session, "outcome_bridge", None) is None:
            self.session.outcome_bridge = getattr(
                self.intelligence_flow,
                "decision_outcome_bridge",
                None
            )

        self.last_completed_cycle = int(
            checkpoint.get("last_completed_cycle", 0)
        )
        return checkpoint
