from dataclasses import asdict, is_dataclass

from core.market_data.operational_action_translator import (
    OperationalActionTranslator
)
from core.market_data.operational_intelligence_adapter import (
    OperationalIntelligenceAdapter
)
from core.market_data.operational_intelligence_context_builder import (
    OperationalIntelligenceContextBuilder
)


class OperationalPaperRuntime:
    """Runs operational market data through intelligence and paper execution."""

    def __init__(
        self,
        market_context_runtime,
        intelligence_flow,
        paper_trading_runtime,
        session_archive=None
    ):
        if market_context_runtime is None:
            raise ValueError(
                "market_context_runtime must not be None"
            )

        if intelligence_flow is None:
            raise ValueError(
                "intelligence_flow must not be None"
            )

        if paper_trading_runtime is None:
            raise ValueError(
                "paper_trading_runtime must not be None"
            )

        self.market_context_runtime = market_context_runtime
        self.intelligence_flow = intelligence_flow
        self.paper_trading_runtime = paper_trading_runtime
        self.session_archive = session_archive

        self.context_builder = (
            OperationalIntelligenceContextBuilder()
        )

        self.adapter = OperationalIntelligenceAdapter()
        self.action_translator = OperationalActionTranslator()

    def run(
        self,
        symbol="BTCUSDT",
        cycles=1,
        continue_on_error=False
    ):
        if cycles <= 0:
            raise ValueError(
                "cycles must be greater than zero"
            )

        results = []

        for cycle_number in range(1, cycles + 1):
            try:
                cycle = self.market_context_runtime.run_cycle(
                    symbol=symbol
                )

                observation = cycle["observation"]
                market_context = cycle["context"]

                if observation is None or market_context is None:
                    results.append({
                        "cycle_number": cycle_number,
                        "observation": observation,
                        "market_context": market_context,
                        "intelligence_context": None,
                        "report": None,
                        "decision": None,
                        "action_proposal": None,
                        "translated_action_proposal": None,
                        "paper_result": None,
                        "error": None
                    })
                    continue

                intelligence_context = (
                    self.context_builder.build(
                        market_context
                    )
                )

                consensus = self.adapter.to_consensus(
                    intelligence_context
                )

                report = self.intelligence_flow.create_report(
                    consensus
                )

                translated_action_proposal = (
                    self.action_translator.translate(
                        report.action_proposal
                    )
                )

                paper_input = {
                    "action_proposal": (
                        translated_action_proposal
                    ),
                    "price": observation.price,
                    "symbol": observation.symbol,
                    "decision": report.decision
                }

                paper_results = (
                    self.paper_trading_runtime.run(
                        cycles=[paper_input],
                        symbol=symbol
                    )
                )

                paper_result = paper_results[0]

                results.append({
                    "cycle_number": cycle_number,
                    "observation": observation,
                    "market_context": market_context,
                    "intelligence_context": intelligence_context,
                    "report": report,
                    "decision": report.decision,
                    "action_proposal": report.action_proposal,
                    "translated_action_proposal": (
                        translated_action_proposal
                    ),
                    "paper_result": paper_result,
                    "error": None
                })

            except Exception as exc:
                if not continue_on_error:
                    raise

                results.append({
                    "cycle_number": cycle_number,
                    "observation": None,
                    "market_context": None,
                    "intelligence_context": None,
                    "report": None,
                    "decision": None,
                    "action_proposal": None,
                    "translated_action_proposal": None,
                    "paper_result": None,
                    "error": exc
                })

        self._archive_session(results)

        return results

    @staticmethod
    def _serialize_value(value):
        if value is None:
            return None

        if is_dataclass(value):
            return OperationalPaperRuntime._serialize_value(
                asdict(value)
            )

        if isinstance(value, dict):
            return {
                str(key): OperationalPaperRuntime._serialize_value(
                    item
                )
                for key, item in value.items()
            }

        if isinstance(value, (list, tuple)):
            return [
                OperationalPaperRuntime._serialize_value(
                    item
                )
                for item in value
            ]

        if isinstance(value, (str, int, float, bool)):
            return value

        if hasattr(value, "__dict__"):
            return {
                str(key): OperationalPaperRuntime._serialize_value(
                    item
                )
                for key, item in vars(value).items()
            }

        return str(value)

    def _build_session_record(self, results):
        summary = self.build_summary(results)

        serializable_summary = (
            self._serialize_value(summary)
        )

        cycles = []

        for result in results:
            paper_result = result.get("paper_result")
            observation = result.get("observation")
            report = result.get("report")
            action_proposal = result.get("action_proposal")

            cycles.append({
                "cycle": result.get("cycle_number"),
                "symbol": getattr(
                    observation,
                    "symbol",
                    None
                ),
                "price": getattr(
                    observation,
                    "price",
                    None
                ),
                "signal": getattr(
                    report,
                    "signal",
                    None
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
                "action": (
                    paper_result.get("action")
                    if paper_result is not None
                    else None
                ),
                "execution_status": (
                    getattr(
                        paper_result.get(
                            "execution_result"
                        ),
                        "status",
                        None
                    )
                    if paper_result is not None
                    else None
                ),
                "realized_pnl": (
                    paper_result.get(
                        "realized_pnl",
                        0.0
                    )
                    if paper_result is not None
                    else None
                ),
                "position_side": getattr(
                    paper_result.get("position")
                    if paper_result is not None
                    else None,
                    "side",
                    None
                ),
                "entry_price": getattr(
                    paper_result.get("position")
                    if paper_result is not None
                    else None,
                    "entry_price",
                    None
                ),
                "quantity": getattr(
                    paper_result.get("position")
                    if paper_result is not None
                    else None,
                    "quantity",
                    None
                ),
                "error": (
                    str(result["error"])
                    if result.get("error") is not None
                    else None
                )
            })

        return {
            "session_id": (
                self.paper_trading_runtime
                .session
                .session_id
            ),
            "cycles": cycles,
            "summary": serializable_summary,
            "final_position": self._serialize_value(
                summary.get("current_position")
            )
        }

    def _archive_session(self, results):
        if self.session_archive is None:
            return None

        session_record = self._build_session_record(
            results
        )

        self.session_archive.save(
            self.paper_trading_runtime.session.session_id,
            session_record
        )

        return session_record

    def build_summary(self, results):
        if results is None:
            raise ValueError(
                "results must not be None"
            )

        paper_results = [
            result["paper_result"]
            for result in results
            if result.get("paper_result") is not None
        ]

        summary = self.paper_trading_runtime.build_summary(
            paper_results
        )

        blind_cycles = sum(
            1
            for result in results
            if (
                result.get("observation") is not None
                and result.get("observation").source_status == "BLIND"
            )
        )

        error_cycles = sum(
            1
            for result in results
            if result.get("error") is not None
        )

        summary["cycles_processed"] = len(results)
        summary["successful_cycles"] = len(paper_results)
        summary["blind_cycles"] = blind_cycles
        summary["error_cycles"] = error_cycles

        return summary
