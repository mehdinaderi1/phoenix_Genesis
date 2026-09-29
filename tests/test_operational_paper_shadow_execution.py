from core.market_data.operational_paper_runtime import OperationalPaperRuntime


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


class FakeShadowRuntime:
    def __init__(self):
        self.cycles = []

    def run(self, cycles, symbol="BTCUSDT"):
        self.cycles.extend(cycles)

        return [{
            "status": "PREPARED",
            "payload": {
                "symbol": symbol,
                "orderSide": "BUY",
                "positionSide": "LONG",
                "orderType": "MARKET",
                "origQty": 0.0002,
            },
            "execution": None,
        } for _ in cycles]


class FakeArchive:
    def save(self, session_id, record):
        self.session_id = session_id
        self.record = record


def test_operational_runtime_preserves_paper_and_shadow_side_by_side():
    market_runtime = FakeMarketContextRuntime()
    intelligence = FakeIntelligenceFlow()
    paper_runtime = FakePaperTradingRuntime()
    shadow_runtime = FakeShadowRuntime()
    archive = FakeArchive()

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

    assert result["shadow_result"]["status"] == "PREPARED"

    assert result["shadow_result"]["payload"]["orderSide"] == "BUY"

    assert result["shadow_result"]["execution"] is None

    assert len(paper_runtime.cycles) == 1
    assert len(shadow_runtime.cycles) == 1
