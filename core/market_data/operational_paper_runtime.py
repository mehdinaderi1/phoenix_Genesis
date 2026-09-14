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
        paper_trading_runtime
    ):
        if market_context_runtime is None:
            raise ValueError("market_context_runtime must not be None")

        if intelligence_flow is None:
            raise ValueError("intelligence_flow must not be None")

        if paper_trading_runtime is None:
            raise ValueError("paper_trading_runtime must not be None")

        self.market_context_runtime = market_context_runtime
        self.intelligence_flow = intelligence_flow
        self.paper_trading_runtime = paper_trading_runtime
        self.context_builder = OperationalIntelligenceContextBuilder()
        self.adapter = OperationalIntelligenceAdapter()

    def run(self, symbol="BTCUSDT", cycles=1):
        if cycles <= 0:
            raise ValueError("cycles must be greater than zero")

        results = []

        for _ in range(cycles):
            cycle = self.market_context_runtime.run_cycle(
                symbol=symbol
            )

            observation = cycle["observation"]
            market_context = cycle["context"]

            if observation is None or market_context is None:
                continue

            intelligence_context = self.context_builder.build(
                market_context
            )

            consensus = self.adapter.to_consensus(
                intelligence_context
            )

            report = self.intelligence_flow.create_report(
                consensus
            )

            paper_input = {
                "action_proposal": report.action_proposal,
                "price": observation.price,
                "symbol": observation.symbol,
                "decision": report.decision
            }

            paper_results = self.paper_trading_runtime.run(
                cycles=[paper_input],
                symbol=symbol
            )

            paper_result = paper_results[0]

            results.append({
                "observation": observation,
                "market_context": market_context,
                "intelligence_context": intelligence_context,
                "report": report,
                "decision": report.decision,
                "action_proposal": report.action_proposal,
                "paper_result": paper_result
            })

        return results
