import json

from core.database import DatabaseManager
from core.market_data.observer import RealMarketObserver
from core.market_data.operational_market_context_runtime import (
    OperationalMarketContextRuntime,
)
from core.market_data.operational_paper_runtime import OperationalPaperRuntime
from core.market_data.pipeline import MarketDataPipeline
from core.market_data.source_manager import MarketDataSourceManager
from execution.http_client import HttpResponse
from execution.paper_session_archive import PaperSessionArchive
from execution.paper_trading_runtime import PaperTradingRuntime
from execution.paper_trading_session import PaperTradingSession
from execution.xt_futures_order_detail_client import XTFuturesOrderDetailClient
from execution.xt_futures_order_detail_transport import (
    XTFuturesOrderDetailTransport,
)
from execution.xt_futures_order_detail_transport_request_builder import (
    XTFuturesOrderDetailTransportRequestBuilder,
)
from execution.xt_futures_order_reconciliation_service import (
    XTFuturesOrderReconciliationService,
)
from execution.xt_futures_position_bridge import XTFuturesPositionBridge
from execution.xt_futures_position_close_bridge import (
    XTFuturesPositionCloseBridge,
)
from execution.xt_futures_shadow_execution_runtime import (
    XTFuturesShadowExecutionRuntime,
)
from execution.xt_futures_transport import XTFuturesTransport
from execution.xt_futures_transport_request_builder import (
    XTFuturesTransportRequestBuilder,
)
from execution.xt_futures_execution_orchestrator import (
    XTFuturesExecutionOrchestrator,
)
from exchanges.xt_exchange import XTExchange
from intelligence.flow import IntelligenceFlow


class ControlledXTExchange(XTExchange):
    def __init__(self):
        super().__init__(timeout=10)
        self.price_calls = 0
        self.kline_calls = 0

    def _request(self, path, params=None):
        if path == "/v4/public/ticker/price":
            self.price_calls += 1
            return {
                "result": [
                    {
                        "s": "btc_usdt",
                        "p": "50000.0",
                    }
                ]
            }

        if path == "/v4/public/kline":
            self.kline_calls += 1

            candles = []

            for index, close in enumerate(
                [50000.0, 50100.0, 50200.0, 50300.0, 50400.0]
            ):
                timestamp_ms = (1000 + index * 300) * 1000

                candles.append(
                    {
                        "t": timestamp_ms,
                        "o": str(close),
                        "h": str(close + 100.0),
                        "l": str(close - 100.0),
                        "c": str(close),
                        "v": "10.0",
                    }
                )

            return {
                "result": candles
            }

        raise AssertionError(f"Unexpected XT endpoint: {path}")


class ControlledOperationalIntelligenceFlow:
    def __init__(self):
        self.real_flow = IntelligenceFlow()
        self.real_flow.enable_inline_outcome_learning = False
        self.calls = 0
        self.decision_outcome_bridge = self.real_flow.decision_outcome_bridge

    def create_report(self, consensus):
        report = self.real_flow.create_report(consensus)

        actions = (
            "PREPARE_LONG",
            "PREPARE_SHORT",
        )

        action = actions[self.calls]
        self.calls += 1

        report.decision.action = action
        report.decision.strategy = {
            "name": "REAL_XT_OPERATIONAL_VALIDATION"
        }

        report.action_proposal = type(
            "ControlledActionProposal",
            (),
            {
                "action": action,
                "status": "APPROVED",
                "reason": f"Controlled validation action: {action}",
                "confidence": 90.0,
                "symbol": "BTCUSDT",
                "strategy": {
                    "name": "REAL_XT_OPERATIONAL_VALIDATION"
                },
                "risk_status": "LOW",
                "metadata": {},
            },
        )()

        return report


class FakeDetailHttpClient:
    def __init__(self):
        self.calls = []

    def get(self, endpoint, headers, timeout=10):
        self.calls.append(
            {
                "endpoint": endpoint,
                "headers": headers,
                "timeout": timeout,
            }
        )

        call_number = len(self.calls)
        order_id = str(100 + call_number)

        price = "50000" if call_number == 1 else "50000"

        return HttpResponse(
            200,
            json.dumps(
                {
                    "rc": 0,
                    "result": {
                        "orderId": order_id,
                        "state": "FILLED",
                        "executedQty": "0.0002",
                        "avgPrice": price,
                    },
                }
            ),
        )


class FakeArchive:
    def save(self, session_id, record):
        self.session_id = session_id
        self.record = record


def build_shadow_runtime(detail_client):
    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=1.0,
    )

    position_bridge = XTFuturesPositionBridge(
        position_manager=session.position_manager,
    )

    position_close_bridge = XTFuturesPositionCloseBridge(
        session=session,
    )

    class FakeCreateHttpClient:
        def __init__(self):
            self.calls = []

        def post(self, endpoint, headers, body, timeout=10):
            self.calls.append(
                {
                    "endpoint": endpoint,
                    "headers": headers,
                    "body": body,
                    "timeout": timeout,
                }
            )

            order_id = str(100 + len(self.calls))

            return HttpResponse(
                200,
                json.dumps(
                    {
                        "rc": 0,
                        "result": {
                            "orderId": order_id,
                        },
                    }
                ),
            )

    create_client = FakeCreateHttpClient()

    create_transport = XTFuturesTransport(
        http_client=create_client,
        timeout=15,
    )

    create_builder = XTFuturesTransportRequestBuilder(
        appkey="APPKEY",
        secret_key="SECRET",
    )

    detail_transport = XTFuturesOrderDetailTransport(
        http_client=detail_client,
        timeout=15,
    )

    detail_builder = XTFuturesOrderDetailTransportRequestBuilder(
        appkey="APPKEY",
        secret_key="SECRET",
        timestamp="1234567890",
    )

    order_detail_client = XTFuturesOrderDetailClient(
        transport=detail_transport,
        request_builder=detail_builder,
    )

    reconciliation_service = XTFuturesOrderReconciliationService(
        detail_client=order_detail_client,
    )

    orchestrator = XTFuturesExecutionOrchestrator(
        reconciliation_service=reconciliation_service,
        position_bridge=position_bridge,
        position_close_bridge=position_close_bridge,
    )

    shadow_runtime = XTFuturesShadowExecutionRuntime(
        balance=1000,
        position_size_percent=1,
        orchestrator=orchestrator,
        transport=create_transport,
        request_builder=create_builder,
        timestamp="1234567890",
    )

    return session, shadow_runtime, create_client


def test_real_xt_market_to_paper_and_shadow_lifecycle(tmp_path):
    database = DatabaseManager(str(tmp_path / "operational.db"))
    database.connect()

    xt = ControlledXTExchange()
    from exchanges.exchange_manager import ExchangeManager

    exchange_manager = ExchangeManager()
    exchange_manager.set_exchange(xt)

    pipeline = MarketDataPipeline(
        exchange_manager,
        database,
    )

    source_manager = MarketDataSourceManager({
        "xt": xt,
    })

    source_manager.set_primary_source("xt")

    observer = RealMarketObserver(source_manager)

    market_runtime = OperationalMarketContextRuntime(
        observer=observer,
        market_data_pipeline=pipeline,
        database=database,
    )

    intelligence = ControlledOperationalIntelligenceFlow()

    paper_session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=1.0,
        outcome_bridge=intelligence.decision_outcome_bridge,
    )

    paper_runtime = PaperTradingRuntime(paper_session)

    detail_client = FakeDetailHttpClient()

    shadow_session, shadow_runtime, create_client = build_shadow_runtime(
        detail_client
    )

    archive = PaperSessionArchive(
        root_path=str(tmp_path / "sessions")
    )

    runtime = OperationalPaperRuntime(
        market_context_runtime=market_runtime,
        intelligence_flow=intelligence,
        paper_trading_runtime=paper_runtime,
        session_archive=archive,
        shadow_execution_runtime=shadow_runtime,
    )

    results = runtime.run(
        symbol="BTCUSDT",
        cycles=2,
    )

    assert len(results) == 2
    assert intelligence.calls == 2

    first = results[0]
    second = results[1]

    assert first["translated_action_proposal"].action == "BUY"
    assert second["translated_action_proposal"].action == "SELL"

    assert first["paper_result"]["action"] == "OPEN"
    assert second["paper_result"]["action"] == "CLOSE"

    assert first["shadow_result"]["status"] == "EXECUTED"
    assert second["shadow_result"]["status"] == "EXECUTED"

    assert (
        first["shadow_result"]["execution"]["reconciliation"].state.value
        == "CONFIRMED"
    )

    assert (
        second["shadow_result"]["execution"]["reconciliation"].state.value
        == "CONFIRMED"
    )

    assert len(create_client.calls) == 2
    assert len(detail_client.calls) == 2

    assert shadow_session.get_position() is None

    assert paper_session.get_position() is None
    assert paper_session.get_trade_count() == 1
    assert paper_session.get_total_pnl() == 0.0

    assert xt.price_calls >= 1
    assert xt.kline_calls >= 1

    database.close()



