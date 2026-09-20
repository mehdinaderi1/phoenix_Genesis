from core.engine import PhoenixEngine
from core.market_data.observer import RealMarketObserver
from core.market_data.operational_market_context_runtime import OperationalMarketContextRuntime
from core.market_data.operational_paper_runtime import OperationalPaperRuntime
from core.market_data.operational_observation_runner import OperationalObservationRunner
from core.market_data.pipeline import MarketDataPipeline
from core.market_data.source_manager import MarketDataSourceManager
from core.market_data.source_candle_pipeline import SourceCandlePipeline
from exchanges.binance_exchange import BinanceExchange
from exchanges.coinmarketcap_source import CoinMarketCapSource
from exchanges.xt_exchange import XTExchange
from exchanges.exchange_manager import ExchangeManager
from exchanges.mock_exchange import MockExchange
from execution.paper_session_archive import PaperSessionArchive
from execution.paper_trading_runtime import PaperTradingRuntime
from execution.paper_trading_session import PaperTradingSession
from intelligence.decision_rules import DecisionRules
from intelligence.flow import IntelligenceFlow


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
    decision = result["decision"]
    action_proposal = result["action_proposal"]
    translated = result["translated_action_proposal"]
    paper_result = result["paper_result"]

    cycle_number = result["cycle_number"]

    if observation is not None and observation.source_status == "BLIND":
        print(
            f"Cycle {cycle_number} | "
            "Price=None | "
            "Source=None | "
            "Status=BLIND | "
            "Market Context=None | "
            "Intelligence=SKIPPED | "
            "Paper=SKIPPED"
        )
        return

    if market_context is None:
        print(
            f"Cycle {cycle_number} | "
            f"Price={observation.price if observation is not None else None} | "
            f"Source={observation.source if observation is not None else None} | "
            f"Status={observation.source_status if observation is not None else 'UNKNOWN'} | "
            "Market Context=None | "
            "Intelligence=SKIPPED | "
            "Paper=SKIPPED"
        )
        return

    report = result.get("report")
    rules = DecisionRules()
    long_gate = rules.can_long(report) if report is not None else False
    short_gate = rules.can_short(report) if report is not None else False

    decision_confidence = (
        getattr(decision, "confidence", None)
        if decision is not None
        else None
    )

    decision_strategy = (
        getattr(decision, "strategy", None)
        if decision is not None
        else None
    )

    if isinstance(decision_strategy, dict):
        decision_strategy = decision_strategy.get("name")

    print(
        f"Cycle {cycle_number} | "
        f"Price={observation.price} | "
        f"Source={observation.source} | "
        f"Trend={market_context.trend} | "
        f"Signal={market_context.signal} | "
        f"ContextConfidence={market_context.confidence:.2f}% | "
        f"Decision={getattr(decision, 'action', None)} | "
        f"DecisionConfidence={decision_confidence} | "
        f"Strategy={decision_strategy} | "
        f"LongGate={'OPEN' if long_gate else 'BLOCKED'} | "
        f"ShortGate={'OPEN' if short_gate else 'BLOCKED'} | "
        f"Proposal={getattr(action_proposal, 'action', None)} | "
        f"Translated={getattr(translated, 'action', None)} | "
        f"Paper={paper_result['action']} | "
        f"PnL={paper_result['realized_pnl']}"
    )

def print_session_summary(summary):
    print()
    print("=" * 60)
    print("PAPER SESSION SUMMARY")
    print("=" * 60)
    print("Cycles Processed:", summary["cycles_processed"])
    print("Successful Cycles:", summary.get("successful_cycles", 0))
    print("BLIND Cycles:", summary.get("blind_cycles", 0))
    print("Error Cycles:", summary.get("error_cycles", 0))
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


def build_real_source_manager():
    xt = XTExchange(timeout=5)
    coinmarketcap = CoinMarketCapSource(timeout=5)

    manager = MarketDataSourceManager({
        "xt": xt,
        "coinmarketcap": coinmarketcap,
    })
    manager.set_primary_source("xt")

    return manager


def main():
    print("PHOENIX GENESIS - OPERATIONAL PROTOTYPE")
    print("=" * 60)
    print("MODE: OBSERVE / PAPER")
    print("REAL ORDERS: DISABLED")
    print("MARKET SOURCES: XT + COINMARKETCAP")
    print("=" * 60)

    engine = PhoenixEngine()
    engine.start()

    # Candle pipeline remains deterministic for the current OBSERVE/PAPER prototype.
    # Real exchange/aggregator price observation is handled by the source manager below.
    exchange_manager = ExchangeManager()
    exchange = MockExchange()
    exchange_manager.set_exchange(exchange)
    exchange_manager.connect()

    configure_market(exchange)

    market_data_pipeline = MarketDataPipeline(
        exchange_manager,
        engine.database,
    )

    source_manager = build_real_source_manager()
    print("DEBUG SOURCE HEALTH:", source_manager.get_healthy_sources())
    print("DEBUG SOURCE PRICES:", source_manager.get_prices("BTCUSDT"))
    source_candle_pipeline = SourceCandlePipeline(
        source_manager=source_manager,
        database=engine.database,
    )

    observer = RealMarketObserver(source_manager)

    market_context_runtime = OperationalMarketContextRuntime(
        observer=observer,
        market_data_pipeline=market_data_pipeline,
        database=engine.database,
        source_candle_pipeline=source_candle_pipeline,
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

    observation_runner = OperationalObservationRunner(
        runtime=operational_runtime
    )

    results = observation_runner.run(
        symbol="BTCUSDT",
        cycles=3,
        interval_seconds=0,
        continue_on_error=True,
    )

    print()
    print("=" * 60)
    print("OPERATIONAL CYCLES")
    print("=" * 60)

    for result in results:
        if result.get("error") is not None:
            print(
                f"Cycle {result.get("cycle_number")} | "
                f"ERROR={result["error"]}"
            )
            continue
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
    print("Market Sources: XT + COINMARKETCAP")
    print("Prototype Cycles:", len(results))
    print("=" * 60)


if __name__ == "__main__":
    main()




