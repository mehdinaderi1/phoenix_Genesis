import os
from notifications.dispatcher import NotificationDispatcher
from notifications.signal_outbox import SignalOutbox
from notifications.signal_publisher import SignalPublisher
from notifications.telegram_sender import TelegramSender
from intelligence.observation.opportunity_observer import OpportunityObserver
from intelligence.observation.opportunity_journal import OpportunityJournal
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
from execution.xt_futures_shadow_execution_runtime import (
    XTFuturesShadowExecutionRuntime
)
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
    paper_result = result.get("paper_result") or {}
    shadow_result = result.get("shadow_result") or {}

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
    operational_strategy = (
        getattr(report, "operational_strategy_result", None)
        if report is not None
        else None
    )

    strategy_allows_long = True
    strategy_allows_short = True

    if operational_strategy is not None:
        strategy_matched = operational_strategy.get("matched", False)
        strategy_signal = operational_strategy.get("signal")
        strategy_allows_long = strategy_matched and strategy_signal == "BUY"
        strategy_allows_short = strategy_matched and strategy_signal == "SELL"

    rules_long = rules.can_long(report) if report is not None else False
    rules_short = rules.can_short(report) if report is not None else False

    long_gate = strategy_allows_long and rules_long
    short_gate = strategy_allows_short and rules_short

    strategy_matched = (
        operational_strategy.get("matched")
        if operational_strategy is not None
        else None
    )
    strategy_signal = (
        operational_strategy.get("signal")
        if operational_strategy is not None
        else None
    )

    print(
        "  GateDetail | "
        f"Signal={getattr(report, 'signal', None)} | "
        f"Risk={getattr(report, 'risk', None)} | "
        f"Confidence={getattr(report, 'confidence', None)} | "
        f"StrategyMatched={strategy_matched} | "
        f"StrategySignal={strategy_signal} | "
        f"RulesLong={rules_long} | "
        f"RulesShort={rules_short} | "
        f"FinalLong={long_gate} | "
        f"FinalShort={short_gate}"
    )

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

    if decision_strategy is None and report is not None:
        operational_strategy = getattr(
            report,
            "operational_strategy_result",
            None
        )

        if isinstance(operational_strategy, dict):
            decision_strategy = operational_strategy.get("strategy")

    if decision_strategy is None and decision is not None:
        champion = getattr(
            decision,
            "champion_strategy",
            None
        )

        if isinstance(champion, dict):
            decision_strategy = champion.get("name")

    if isinstance(decision_strategy, dict):
        decision_strategy = decision_strategy.get("name")

    breakdown = getattr(
        market_context,
        "consensus_breakdown",
        None,
    )

    print(
        f"Cycle {cycle_number} | "
        f"Price={observation.price if observation is not None else None} | "
        f"Source={observation.source if observation is not None else None} | "
        f"Trend={market_context.trend} | "
        f"Signal={market_context.signal} | "
        f"ContextConfidence={market_context.confidence:.2f}% | "
        f"Decision={getattr(decision, 'action', None)} | "
        f"DecisionConfidence={decision_confidence} | "
        f"Strategy={decision_strategy} | "
        f"LongGate={'OPEN' if long_gate else 'BLOCKED'} | "
        f"ShortGate={'OPEN' if short_gate else 'BLOCKED'} | "
        f"Proposal={getattr(action_proposal, 'action', None)}/"
        f"{getattr(action_proposal, 'status', None)} | "
        f"ProposalReason={getattr(action_proposal, 'reason', None)} | "
        f"Translated={getattr(translated, 'action', None)}/"
        f"{getattr(translated, 'status', None)} | "
        f"TranslatedReason={getattr(translated, 'reason', None)} | "
        f"Paper={paper_result.get('action')} | "
        f"Shadow={shadow_result.get('status', 'SKIPPED')} | "
        f"PnL={paper_result.get('realized_pnl')}"
    )

    if breakdown:
        print(
            f"  Consensus | "
            f"Weighted={breakdown['weighted_confidence']:.2f} | "
            f"Conflict={breakdown['signal_conflict']} | "
            f"Penalty={breakdown['conflict_penalty']} | "
            f"Final={breakdown['final_confidence']:.2f}"
        )

        for item in breakdown["timeframes"]:
            reasons = item.get("reasons", [])
            reason_text = ", ".join(reasons) if reasons else "Not available"

            print(
                f"  MTF {item['timeframe']} | "
                f"Signal={item['signal']} | "
                f"Confidence={item['confidence']:.2f} | "
                f"Weight={item['weight']} | "
                f"Reasons={reason_text}"
            )

    print(
        f"  NotificationError={result.get('notification_error')} | "
        f"Primary5mBoundaryPresent="
        f"{isinstance(result.get('candle_boundaries', {}).get('5m'), dict)}"
    )

    candle_boundaries = result.get("candle_boundaries", {})

    if candle_boundaries:
        for timeframe, boundary in candle_boundaries.items():
            if boundary is None:
                print(f"  {timeframe} | CandleBoundary=None")
                continue

            print(
                f"  {timeframe} | "
                f"CandleStart={boundary["candle_start"]} | "
                f"NextBoundary={boundary["next_boundary"]} | "
                f"Age={boundary["age_seconds"]} | "
                f"Closed={boundary["is_closed"]}"
            )


def print_session_summary(summary):
    print()
    print("=" * 60)
    print("PAPER SESSION SUMMARY")
    print("=" * 60)
    print("Cycles Processed:", summary["cycles_processed"])
    print("Successful Cycles:", summary.get("successful_cycles", 0))
    print("BLIND Cycles:", summary.get("blind_cycles", 0))
    print("No-Data Cycles:", summary.get("no_data_cycles", 0))
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
    market_data_pipeline = None

    source_manager = build_real_source_manager()
    print("DEBUG SOURCE HEALTH:", source_manager.get_healthy_sources())
    print("DEBUG SOURCE PRICES:", source_manager.get_prices("BTCUSDT"))

    source_candle_pipeline = SourceCandlePipeline(
        source_manager=source_manager,
        database=engine.database,
    )

    timeframes = ("5m", "15m", "30m", "4H", "1D")

    warm_up_results = source_candle_pipeline.warm_up(
        symbol="BTCUSDT",
        timeframes=timeframes,
        limit=30,
    )

    print("Historical MTF warm-up:", warm_up_results)

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

    shadow_runtime = XTFuturesShadowExecutionRuntime(
        balance=paper_session.initial_balance,
        position_size_percent=paper_session.position_size_percent,
    )

    session_archive = PaperSessionArchive(
        root_path="data/paper_sessions"
    )

    notification_outbox = SignalOutbox(
        "data/phoenix_notifications.db"
    )
    signal_publisher = SignalPublisher(
        notification_outbox,
        primary_timeframe="5m",
    )

    opportunity_observer = OpportunityObserver()
    opportunity_journal = OpportunityJournal(
        "data/opportunities.jsonl"
    )

    operational_runtime = OperationalPaperRuntime(
        market_context_runtime=market_context_runtime,
        intelligence_flow=intelligence_flow,
        paper_trading_runtime=paper_runtime,
        session_archive=session_archive,
        shadow_execution_runtime=shadow_runtime,
        signal_publisher=signal_publisher,
        opportunity_observer=opportunity_observer,
        opportunity_journal=opportunity_journal,
    )

    print()
    print("Starting operational cycles...")

    observation_runner = OperationalObservationRunner(
        runtime=operational_runtime
    )

    timeframes = ("5m", "15m", "30m", "4H", "1D")

    observation_cycles = int(
        os.environ.get("PHOENIX_OBSERVATION_CYCLES", "20")
    )
    observation_interval_seconds = float(
        os.environ.get("PHOENIX_OBSERVATION_INTERVAL_SECONDS", "0")
    )

    results = observation_runner.run(
        symbol="BTCUSDT",
        cycles=observation_cycles,
        interval_seconds=observation_interval_seconds,
        continue_on_error=True,
        timeframes=timeframes,
    )

    print()
    print("=" * 60)
    print("OPERATIONAL CYCLES")
    print("=" * 60)

    for result in results:
        if result.get("error") is not None:
            print(
                f"Cycle {result.get('cycle_number')} | "
                f"ERROR={result['error']}"
            )
            continue

        print_cycle(result)

    print()
    print("=" * 60)
    print("TELEGRAM SIGNAL OUTBOX")
    print("=" * 60)

    if os.environ.get("PHOENIX_TELEGRAM_ENABLED", "0").strip() == "1":
        try:
            dispatcher = NotificationDispatcher(
                outbox=notification_outbox,
                sender=TelegramSender(),
            )
            dispatch_result = dispatcher.dispatch_due_messages()
            print("Telegram dispatch:", dispatch_result)
        except ValueError as exc:
            print("Telegram dispatch skipped:", str(exc))
        except Exception as exc:
            print(
                "Telegram dispatch error:",
                f"{type(exc).__name__}: {exc}",
            )
    else:
        print("Telegram dispatch disabled; pending messages preserved.")

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
