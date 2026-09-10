from core.engine import PhoenixEngine
from exchanges.exchange_manager import ExchangeManager
from exchanges.mock_exchange import MockExchange
from market.market_data_engine import MarketDataEngine
from market.market_data_reader import MarketDataReader
from core.market_data.pipeline import MarketDataPipeline
from analysis.multi_timeframe_pipeline import MultiTimeframePipeline
from intelligence.flow import IntelligenceFlow

from execution.paper_trading_session import PaperTradingSession
from execution.paper_position_lifecycle import PaperPositionLifecycle


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
    # Paper Trading Session
    # ---------------------------------------------------------

    paper_session = PaperTradingSession(
        initial_balance=1000,
        position_size_percent=1
    )

    lifecycle = PaperPositionLifecycle(
        paper_session
    )

    # ---------------------------------------------------------
    # Paper Position Lifecycle
    # ---------------------------------------------------------

    lifecycle_result = lifecycle.process(
        action_proposal=report.action_proposal,
        price=price,
        symbol="BTCUSDT"
    )

    lifecycle_action = lifecycle_result["action"]

    execution_result = lifecycle_result.get(
        "execution_result"
    )

    position = lifecycle_result.get(
        "position"
    )

    print("==============================")
    print("🦅 Phoenix Paper Lifecycle")
    print("==============================")

    print("Lifecycle:", lifecycle_action)

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