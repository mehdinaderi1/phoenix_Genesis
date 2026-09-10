from core.engine import PhoenixEngine
from exchanges.exchange_manager import ExchangeManager
from exchanges.mock_exchange import MockExchange
from market.market_data_engine import MarketDataEngine
from core.market_data.pipeline import MarketDataPipeline
from analysis.multi_timeframe_pipeline import MultiTimeframePipeline
from intelligence.flow import IntelligenceFlow
from execution.paper_trading_session import PaperTradingSession


def test_intelligence_action_proposal_flows_into_paper_session():

    engine = PhoenixEngine()
    engine.start()

    exchange_manager = ExchangeManager()

    mock = MockExchange()
    exchange_manager.set_exchange(mock)

    assert exchange_manager.connect()

    price = exchange_manager.get_price("BTCUSDT")

    pipeline = MarketDataPipeline(
        exchange_manager,
        engine.database
    )

    multi_timeframe_pipeline = MultiTimeframePipeline(
        engine.database
    )

    for timeframe in ("30m", "4H", "1D"):
        pipeline.fetch_and_store_historical(
            symbol="BTCUSDT",
            timeframe=timeframe,
            limit=30
        )

    consensus = multi_timeframe_pipeline.analyze(
        "BTCUSDT"
    )

    intelligence_flow = IntelligenceFlow()

    report = intelligence_flow.create_report(
        consensus
    )

    assert report.action_proposal is not None

    paper_session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=1.0
    )

    result = paper_session.process_action(
        action_proposal=report.action_proposal,
        price=price,
        symbol="BTCUSDT"
    )

    execution_result = result["execution_result"]

    assert execution_result is not None
    assert execution_result.symbol == "BTCUSDT"
    assert execution_result.price == price

    assert (
        execution_result.action
        == report.action_proposal.action
    )

    assert paper_session.get_position() is None
    assert paper_session.get_balance() == 1000.0
    assert paper_session.get_total_pnl() == 0.0
    assert paper_session.get_trade_count() == 0