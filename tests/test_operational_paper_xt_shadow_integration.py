from core.market_data.operational_paper_runtime import OperationalPaperRuntime
from execution.http_client import HttpResponse
from execution.xt_futures_shadow_execution_runtime import XTFuturesShadowExecutionRuntime
from execution.xt_futures_transport import XTFuturesTransport
from execution.xt_futures_transport_request_builder import XTFuturesTransportRequestBuilder


class FakeObservation:
    symbol = "BTCUSDT"
    price = 50000.0
    source_status = "LIVE"


class FakeMarketContext:
    symbol = "BTCUSDT"
    trend = "BULLISH"
    signal = "BUY"
    confidence = 90
    consensus_breakdown = {}


class FakeMarketContextRuntime:
    def run_cycle(self, symbol="BTCUSDT", timeframes=None):
        return {
            "observation": FakeObservation(),
            "context": FakeMarketContext(),
            "candle_boundaries": {},
        }


class FakeIntelligenceFlow:
    def create_report(self, consensus):
        from intelligence.action_proposal import ActionProposal

        proposal = ActionProposal(
            action="PREPARE_LONG",
            status="APPROVED",
            symbol="BTCUSDT",
            confidence=90,
            reason="approved integration test",
        )

        class Report:
            action_proposal = proposal
            decision = None
            signal = "BUY"
            trend = "BULLISH"
            regime = "TREND"
            confidence = 90
            risk = "LOW"

        return Report()


class FakePaperTradingRuntime:
    def __init__(self):
        self.cycles = []

        class Session:
            session_id = "test-session"

        self.session = Session()

    def run(self, cycles, symbol="BTCUSDT"):
        self.cycles.extend(cycles)

        return [{
            "action": "BUY",
            "position": None,
            "realized_pnl": 0.0,
            "learning_result": None,
        } for _ in cycles]

    def build_summary(self, paper_results):
        return {
            "current_position": None,
            "realized_pnl": 0.0,
        }


class FakeHttpClient:
    def __init__(self):
        self.calls = []

    def post(self, endpoint, headers, body, timeout=10):
        self.calls.append({
            "endpoint": endpoint,
            "headers": headers,
            "body": body,
            "timeout": timeout,
        })

        return HttpResponse(
            200,
            '{"rc":0,"result":{"orderId":"123"}}',
        )


class FakeArchive:
    def save(self, session_id, record):
        self.session_id = session_id
        self.record = record


def test_operational_runtime_connects_real_shadow_runtime():
    market_runtime = FakeMarketContextRuntime()
    intelligence = FakeIntelligenceFlow()
    paper_runtime = FakePaperTradingRuntime()
    archive = FakeArchive()

    http_client = FakeHttpClient()

    transport = XTFuturesTransport(
        http_client=http_client,
        timeout=15,
    )

    request_builder = XTFuturesTransportRequestBuilder(
        appkey="APPKEY",
        secret_key="SECRET",
    )

    shadow_runtime = XTFuturesShadowExecutionRuntime(
        balance=1000,
        position_size_percent=1,
        transport=transport,
        request_builder=request_builder,
        timestamp="1234567890",
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
        cycles=1,
    )

    assert len(results) == 1

    result = results[0]

    assert result["paper_result"]["action"] == "BUY"

    assert result["shadow_result"]["status"] == "EXECUTED"

    assert result["shadow_result"]["execution"]["execution"]["state"] == "SENT"

    assert result["shadow_result"]["execution"]["execution"]["order_id"] == "123"

    assert len(http_client.calls) == 1

    assert http_client.calls[0]["endpoint"] == (
        "/future/trade/v1/order/create"
    )

    assert http_client.calls[0]["headers"]["validate-appkey"] == "APPKEY"
    assert http_client.calls[0]["headers"]["validate-timestamp"] == "1234567890"

    assert len(paper_runtime.cycles) == 1
