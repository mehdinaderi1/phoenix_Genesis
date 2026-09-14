from core.engine import PhoenixEngine
from core.market_data.market_data import MarketData
from core.market_data.observer import RealMarketObserver
from core.market_data.operational_market_context_runtime import OperationalMarketContextRuntime
from core.market_data.operational_paper_runtime import OperationalPaperRuntime
from core.market_data.pipeline import MarketDataPipeline
from exchanges.exchange_manager import ExchangeManager
from exchanges.mock_exchange import MockExchange
from execution.paper_session_archive import PaperSessionArchive
from execution.paper_trading_runtime import PaperTradingRuntime
from execution.paper_trading_session import PaperTradingSession
from intelligence.flow import IntelligenceFlow


class PrototypeSourceManager:
    """Deterministic OBSERVE source used by the local paper prototype."""

    def __init__(self):
        self.prices = [65000.0, 65500.0, 66000.0]
        self.index = 0

    def get_price(self, symbol):
        if self.index >= len(self.prices):
            price = self.prices[-1]
        else:
            price = self.prices[self.index]
            self.index += 1

        return MarketData(
            symbol=symbol,
            price=price,
            source="prototype",
            fallback_used=False,
            source_status="HEALTHY",
        )


def configure_market(exchange):
    candle = {
        "timestamp": 1001,
        "open": 65000,
        "high": 65100,
        "low": 64900,
        "close": 65000,
        "volume": 1,
    }

    for timeframe in ("30m", "4H", "1D"):
        exchange.set_candle_sequence(
            "BTCUSDT",
            timeframe,
            [candle],
        )


def print_cycle(result):
    observation = result["observation"]
    market_context = result["market_context"]
    report = result["report"]
    decision = result["decision"]
    action_proposal = result["action_proposal"]
    translated = result["translated_action_proposal"]
    paper_result = result["paper_result"]

    print(
        f"Cycle {result["cycle_number"]} | "
        f"Price={observation.price} | "
        f"Source={observation.source} | "
        f"Trend={market_context.trend} | "
        f"Signal={market_context.signal} | "
        f"Confidence={market_context.confidence:.2f}% | "
        f"Decision={getattr(decision, "action", None)} | "
        f"Proposal={getattr(action_proposal, "action", None)} | "
        f"Translated={getattr(translated, "action", None)} | "
        f"Paper={paper_result["action"]} | "
        f"PnL={paper_result["realized_pnl"]}"
    )


def print_session_summary(summary):
    print()
    print("=" * 60)
    print("PAPER SESSION SUMMARY")
    print("=" * 60)
    print("Cycles Processed:", summary["cycles_processed"])
    print("OPEN:", summary["open_count"])
    print("HOLD:", summary["hold_count"])
    print("CLOSE:", summary["close_count"])
    print("Balance:", summary["balance"])
    print("Total PnL:", summary["total_pnl"])
    print("Trades:", summary["trade_count"])
    print(
        "Final Position:",
        "NONE"
        if summary["current_position"] is None
        else summary["current_position"]
    )


def print_learning_summary(intelligence_flow):
    experiences = intelligence_flow.experience_memory.experiences

    print()
    print("=" * 60)
    print("LEARNING")
    print("=" * 60)
    print("Experiences:", len(experiences))

    for index, experience in enumerate(experiences, start=1):
        print(
            f"Experience {index} | "
            f"Success={experience.success} | "
            f"Score={experience.score} | "
            f"Strategy={experience.strategy}"
        )


def main():
    print("PHOENIX GENESIS - OPERATIONAL PROTOTYPE")
    print("=" * 60)
    print("MODE: OBSERVE / PAPER")
    print("REAL ORDERS: DISABLED")
    print("=" * 60)

    engine = PhoenixEngine()
    engine.start()

    exchange_manager = ExchangeManager()
    exchange = MockExchange()
    exchange_manager.set_exchange(exchange)
    exchange_manager.connect()

    configure_market(exchange)

    market_data_pipeline = MarketDataPipeline(
        exchange_manager,
        engine.database,
    )

    source_manager = PrototypeSourceManager()
    observer = RealMarketObserver(source_manager)

    market_context_runtime = OperationalMarketContextRuntime(
        observer=observer,
        market_data_pipeline=market_data_pipeline,
        database=engine.database,
    )

    intelligence_flow = IntelligenceFlow()
    intelligence_flow.enable_inline_outcome_learning = False

    paper_session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=1.0,
        outcome_bridge=intelligence_flow.decision_outcome_bridge,
    )

    paper_runtime = PaperTradingRuntime(
        session=paper_session
    )

    session_archive = PaperSessionArchive(
        root_path="data/paper_sessions"
    )

    operational_runtime = OperationalPaperRuntime(
        market_context_runtime=market_context_runtime,
        intelligence_flow=intelligence_flow,
        paper_trading_runtime=paper_runtime,
        session_archive=session_archive,
    )

    print()
    print("Starting operational cycles...")

    results = operational_runtime.run(
        symbol="BTCUSDT",
        cycles=3,
        continue_on_error=False,
    )

    print()
    print("=" * 60)
    print("OPERATIONAL CYCLES")
    print("=" * 60)

    for result in results:
        print_cycle(result)

    summary = operational_runtime.build_summary(results)

    print_session_summary(summary)
    print_learning_summary(intelligence_flow)

    print()
    print("=" * 60)
    print("ARCHIVE")
    print("=" * 60)
    print("Session ID:", paper_session.session_id)
    print("Archive Root: data/paper_sessions")
    print("Session Archived: YES")

    print()
    print("=" * 60)
    print("PROTOTYPE STATUS")
    print("=" * 60)
    print("Operational Runtime: ACTIVE")
    print("Market Mode: OBSERVE")
    print("Execution Mode: PAPER")
    print("Real Orders: DISABLED")
    print("Prototype Cycles:", len(results))
    print("=" * 60)


if __name__ == "__main__":
    main()
