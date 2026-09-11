from core.engine import PhoenixEngine
from exchanges.exchange_manager import ExchangeManager
from exchanges.mock_exchange import MockExchange
from market.market_data_engine import MarketDataEngine
from market.market_data_reader import MarketDataReader
from core.market_data.pipeline import MarketDataPipeline
from analysis.multi_timeframe_pipeline import MultiTimeframePipeline
from intelligence.flow import IntelligenceFlow
from execution.paper_trading_session import PaperTradingSession
from execution.paper_market_cycle_runner import PaperMarketCycleRunner
from execution.paper_session_archive import PaperSessionArchive
from execution.paper_trading_runtime import PaperTradingRuntime
def main():
    print("🦅 Phoenix Genesis Starting...")
    engine = PhoenixEngine()
    engine.start()
    exchange_manager = ExchangeManager()
    mock = MockExchange()
    exchange_manager.set_exchange(mock)
    print(exchange_manager.connect())
    price = exchange_manager.get_price("BTCUSDT")
    print(f"BTC Price: {price}")
    balance = exchange_manager.get_balance()
    print(f"Balance: {balance}")
    pipeline = MarketDataPipeline(
        exchange_manager,
        engine.database
    )
    # ---------------------------------------------------------
    # Multi Timeframe Analysis
    # ---------------------------------------------------------
    multi_timeframe_pipeline = MultiTimeframePipeline(
        engine.database
    )
    print("\n📚 Loading historical market data...")
    for timeframe in ("30m", "4H", "1D"):
        stored = pipeline.fetch_and_store_historical(
            symbol="BTCUSDT",
            timeframe=timeframe,
            limit=30
        )
        print(
            f"   {timeframe}: "
            f"{len(stored)} historical candles stored"
        )
    print("\n🧠 Analyzing historical market data...")
    consensus = multi_timeframe_pipeline.analyze(
        "BTCUSDT"
    )
    print("==============================")
    print("🦅 Phoenix Market Consensus")
    print("==============================")
    print(consensus.summary())
    # ---------------------------------------------------------
    # Intelligence Flow
    # ---------------------------------------------------------
    intelligence_flow = IntelligenceFlow()
    report = intelligence_flow.create_report(
        consensus
    )
    print("==============================")
    print("🦅 Phoenix Intelligence Report")
    print("==============================")
    print(report)
    # ---------------------------------------------------------
    # Paper Trading Runtime
    # ---------------------------------------------------------
    paper_session = PaperTradingSession(
        initial_balance=1000,
        position_size_percent=1
    )
    paper_session_archive = PaperSessionArchive(
        root_path="data/paper_sessions"
    )
    paper_cycle_runner = PaperMarketCycleRunner(
        exchange_manager=exchange_manager,
        multi_timeframe_pipeline=multi_timeframe_pipeline,
        intelligence_flow=intelligence_flow,
        session=paper_session,
        session_archive=paper_session_archive
    )
    # One real intelligence cycle.
    # Additional market cycles can be appended here later
    # without recreating the paper session.
    runtime_results = paper_cycle_runner.run(
        cycle_count=3,
        symbol="BTCUSDT"
    )
    runtime_summary = paper_cycle_runner.build_summary(
        runtime_results
    )
    runtime_records = paper_cycle_runner.build_cycle_records(
        runtime_results
    )
    runtime_session_record = (
        paper_cycle_runner.save_session(
            runtime_results
        )
    )
    lifecycle_result = runtime_results[-1]
    lifecycle_action = lifecycle_result["action"]
    execution_result = lifecycle_result.get(
        "execution_result"
    )
    position = lifecycle_result.get(
        "position"
    )
    # ---------------------------------------------------------
    # Paper Lifecycle
    # ---------------------------------------------------------
    print("==============================")
    print("🦅 Phoenix Paper Lifecycle")
    print("==============================")
    print("Cycles:", runtime_summary["cycles_processed"])
    print("OPEN:", runtime_summary["open_count"])
    print("HOLD:", runtime_summary["hold_count"])
    print("CLOSE:", runtime_summary["close_count"])
    print("Lifecycle:", lifecycle_action)
    # ---------------------------------------------------------
    # Paper Cycle Records
    # ---------------------------------------------------------
    print("==============================")
    print("🦅 Phoenix Paper Cycle Records")
    print("==============================")
    for record in runtime_records:
        print(
            f"Cycle {record['cycle']} | "
            f"{record['symbol']} | "
            f"Price: {record['price']} | "
            f"Action: {record['action']} | "
            f"Realized PnL: {record['realized_pnl']}"
        )
    # ---------------------------------------------------------
    # Paper Runtime Session Record
    # ---------------------------------------------------------
    print("==============================")
    print("🦅 Phoenix Paper Runtime Session Record")
    print("==============================")
    print(
        "Cycles:",
        len(runtime_session_record["cycles"])
    )
    print(
        "Cycles Processed:",
        runtime_session_record["summary"][
            "cycles_processed"
        ]
    )
    print(
        "Balance:",
        runtime_session_record["summary"][
            "balance"
        ]
    )
    print(
        "Total PnL:",
        runtime_session_record["summary"][
            "total_pnl"
        ]
    )
    print(
        "Trades:",
        runtime_session_record["summary"][
            "trade_count"
        ]
    )
    print(
        "Final Position:",
        runtime_session_record["final_position"]
    )
    # ---------------------------------------------------------
    # Paper End-to-End Scenario
    # ---------------------------------------------------------
    scenario_session = PaperTradingSession(
        initial_balance=1000,
        position_size_percent=10
    )
    scenario_runtime = PaperTradingRuntime(
        session=scenario_session
    )
    scenario_cycles = [
        {
            "action_proposal": type(
                "ScenarioActionProposal",
                (),
                {
                    "action": "BUY",
                    "status": "APPROVED",
                    "reason": "End-to-end scenario OPEN",
                }
            )(),
            "price": 65000.0,
            "symbol": "BTCUSDT"
        },
        {
            "action_proposal": type(
                "ScenarioActionProposal",
                (),
                {
                    "action": "WAIT",
                    "status": "APPROVED",
                    "reason": "End-to-end scenario HOLD",
                }
            )(),
            "price": 65500.0,
            "symbol": "BTCUSDT"
        },
        {
            "action_proposal": type(
                "ScenarioActionProposal",
                (),
                {
                    "action": "SELL",
                    "status": "APPROVED",
                    "reason": "End-to-end scenario CLOSE",
                }
            )(),
            "price": 66000.0,
            "symbol": "BTCUSDT"
        }
    ]
    scenario_results = scenario_runtime.run(
        cycles=scenario_cycles,
        symbol="BTCUSDT"
    )
    scenario_summary = (
        scenario_runtime.build_summary(
            scenario_results
        )
    )
    print("==============================")
    print("🦅 Phoenix Paper End-to-End Scenario")
    print("==============================")
    for index, result in enumerate(
        scenario_results,
        start=1
    ):
        print(
            f"Cycle {index} | "
            f"Action: {result['action']} | "
            f"Price: {scenario_cycles[index - 1]['price']} | "
            f"Realized PnL: {result['realized_pnl']}"
        )
    print(
        "Final Position:",
        "NONE"
        if scenario_summary["current_position"] is None
        else scenario_summary["current_position"]
    )
    print(
        "Balance:",
        scenario_summary["balance"]
    )
    print(
        "Total PnL:",
        scenario_summary["total_pnl"]
    )
    print(
        "Trades:",
        scenario_summary["trade_count"]
    )
    # ---------------------------------------------------------
    # Paper Execution
    # ---------------------------------------------------------
    print("==============================")
    print("🦅 Phoenix Paper Execution")
    print("==============================")
    if execution_result is None:
        print("Status: NOT_EXECUTED")
        print("Action:", report.action_proposal.action)
        print("Symbol:", "BTCUSDT")
        print("Price:", price)
        print("Quantity:", None)
        print("Reason:", report.action_proposal.reason)
    else:
        print("Status:", execution_result.status)
        print("Action:", execution_result.action)
        print("Symbol:", execution_result.symbol)
        print("Price:", execution_result.price)
        print("Quantity:", execution_result.quantity)
        print("Reason:", execution_result.reason)
    # ---------------------------------------------------------
    # Paper Position
    # ---------------------------------------------------------
    print("==============================")
    print("🦅 Phoenix Paper Position")
    print("==============================")
    if position is None:
        print("Position: NONE")
        print("PnL: 0.0")
    else:
        print("Symbol:", position.symbol)
        print("Side:", position.side)
        print("Entry Price:", position.entry_price)
        print("Quantity:", position.quantity)
        pnl = paper_session.position_manager.calculate_pnl(
            price
        )
        print("Unrealized PnL:", pnl)
    # ---------------------------------------------------------
    # Paper Portfolio
    # ---------------------------------------------------------
    realized_pnl = lifecycle_result.get(
        "realized_pnl",
        0.0
    )
    print("==============================")
    print("🦅 Phoenix Paper Portfolio")
    print("==============================")
    print(
        "Initial Balance:",
        paper_session.portfolio.initial_balance
    )
    print(
        "Realized PnL:",
        realized_pnl
    )
    print(
        "Virtual Balance:",
        paper_session.get_balance()
    )
    print(
        "Total PnL:",
        paper_session.get_total_pnl()
    )
    # ---------------------------------------------------------
    # Paper Trade History
    # ---------------------------------------------------------
    print("==============================")
    print("🦅 Phoenix Paper Trade History")
    print("==============================")
    print(
        "Trades:",
        paper_session.get_trade_count()
    )
    print(
        "Total Realized PnL:",
        paper_session.trade_history.get_total_realized_pnl()
    )
    # ---------------------------------------------------------
    # Current Market Data
    # ---------------------------------------------------------
    multi_data = pipeline.fetch_multi_timeframes(
        "BTCUSDT"
    )
    print("==============================")
    print("🦅 Phoenix Multi Timeframe Data")
    print("==============================")
    for timeframe, candle in multi_data.items():
        print(f"\nTimeframe: {timeframe}")
        if candle:
            print("Close:", candle["close"])
            print("Volume:", candle["volume"])
    market_engine = MarketDataEngine(
        exchange_manager,
        engine.database
    )
    candle = market_engine.get_candle("BTCUSDT")
    print("==============================")
    print("🦅 Phoenix Market Data")
    print("==============================")
    print(candle)
    print("Close Price:", candle.close)
    print("Volume:", candle.volume)
    reader = MarketDataReader(
        engine.database
    )
    print("==============================")
    print("🦅 Phoenix Timeframe Test")
    print("==============================")
    prices_1m = reader.get_close_prices(
        "BTCUSDT",
        "1m"
    )
    prices_4h = reader.get_close_prices(
        "BTCUSDT",
        "4H"
    )
    prices_1d = reader.get_close_prices(
        "BTCUSDT",
        "1D"
    )
    print("1m prices:", prices_1m)
    print("4H prices:", prices_4h)
    print("1D prices:", prices_1d)
    latest = reader.get_latest_candle(
        "BTCUSDT"
    )
    print("==============================")
    print("🦅 Latest Phoenix Candle")
    print("==============================")
    print(latest)
    candles = engine.database.get_candles()
    print("==============================")
    print("🦅 Stored Market Candles")
    print("==============================")
    for item in candles:
        print(item)
if __name__ == "__main__":
    main()
