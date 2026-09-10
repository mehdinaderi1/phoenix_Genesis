from core.engine import PhoenixEngine
from exchanges.exchange_manager import ExchangeManager
from exchanges.mock_exchange import MockExchange
from market.market_data_engine import MarketDataEngine
from market.market_data_reader import MarketDataReader
from core.market_data.pipeline import MarketDataPipeline
from analysis.multi_timeframe_pipeline import MultiTimeframePipeline
from intelligence.flow import IntelligenceFlow

from execution.paper_execution_engine import PaperExecutionEngine
from execution.paper_portfolio import PaperPortfolio
from execution.paper_trade_history import PaperTradeHistory
from execution.paper_position_manager import PaperPositionManager


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
    # Paper Trading Components
    # ---------------------------------------------------------

    paper_portfolio = PaperPortfolio.create(
        initial_balance=1000
    )

    paper_trade_history = PaperTradeHistory()

    paper_position_manager = PaperPositionManager()

    paper_execution_engine = PaperExecutionEngine()

    # ---------------------------------------------------------
    # Paper Execution
    # ---------------------------------------------------------

    execution_result = paper_execution_engine.execute(
        report.action_proposal,
        price=price,
        symbol="BTCUSDT",
        balance=paper_portfolio.get_balance(),
        position_size_percent=1
    )

    print("==============================")
    print("🦅 Phoenix Paper Execution")
    print("==============================")

    print("Status:", execution_result.status)
    print("Action:", execution_result.action)
    print("Symbol:", execution_result.symbol)
    print("Price:", execution_result.price)
    print("Quantity:", execution_result.quantity)
    print("Reason:", execution_result.reason)

    # ---------------------------------------------------------
    # Paper Position
    # ---------------------------------------------------------

    position = paper_position_manager.open_position(
        execution_result
    )

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

        pnl = paper_position_manager.calculate_pnl(
            price
        )

        print("Unrealized PnL:", pnl)

    # ---------------------------------------------------------
    # Paper Portfolio + Trade History
    # ---------------------------------------------------------

    realized_pnl = 0.0

    if position is not None:

        closed = paper_position_manager.close_position_with_pnl(
            current_price=price
        )

        if closed is not None:

            realized_pnl = closed["realized_pnl"]

            paper_portfolio.apply_realized_pnl(
                realized_pnl
            )

            paper_trade_history.add_trade(
                position=closed["position"],
                exit_price=closed["exit_price"],
                realized_pnl=closed["realized_pnl"]
            )

    print("==============================")
    print("🦅 Phoenix Paper Portfolio")
    print("==============================")

    print(
        "Initial Balance:",
        paper_portfolio.initial_balance
    )

    print(
        "Realized PnL:",
        realized_pnl
    )

    print(
        "Virtual Balance:",
        paper_portfolio.get_balance()
    )

    print(
        "Total PnL:",
        paper_portfolio.get_total_pnl()
    )

    print("==============================")
    print("🦅 Phoenix Paper Trade History")
    print("==============================")

    print(
        "Trades:",
        paper_trade_history.get_trade_count()
    )

    print(
        "Total Realized PnL:",
        paper_trade_history.get_total_realized_pnl()
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