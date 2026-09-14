from core.market_data.operational_intelligence_adapter import (
    OperationalIntelligenceAdapter
)
from core.market_data.operational_intelligence_context_builder import (
    OperationalIntelligenceContextBuilder
)


class OperationalIntelligenceRuntime:
    """Runs operational market context through Phoenix intelligence."""

    def __init__(self, market_context_runtime, intelligence_flow):
        if market_context_runtime is None:
            raise ValueError("market_context_runtime must not be None")
        if intelligence_flow is None:
            raise ValueError("intelligence_flow must not be None")

        self.market_context_runtime = market_context_runtime
        self.intelligence_flow = intelligence_flow
        self.context_builder = OperationalIntelligenceContextBuilder()
        self.adapter = OperationalIntelligenceAdapter()

    def run(self, symbol="BTCUSDT", cycles=1):
        contexts = self.market_context_runtime.run(
            symbol=symbol,
            cycles=cycles
        )

        results = []

        for market_context in contexts:
            intelligence_context = self.context_builder.build(
                market_context
            )

            consensus = self.adapter.to_consensus(
                intelligence_context
            )

            report = self.intelligence_flow.create_report(
                consensus
            )

            results.append({
                "market_context": market_context,
                "intelligence_context": intelligence_context,
                "report": report,
                "decision": report.decision,
                "action_proposal": report.action_proposal
            })

        return results
