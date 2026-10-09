from execution.paper_market_cycle_runner import PaperMarketCycleRunner
from execution.paper_session_archive import PaperSessionArchive
from execution.paper_trading_session import PaperTradingSession


class FakeExchangeManager:
    def __init__(self):
        self.calls = []

    def get_price(self, symbol):
        self.calls.append(symbol)
        return 65000.0 + len(self.calls)


class FakeMultiTimeframePipeline:
    def __init__(self):
        self.calls = 0

    def analyze(self, symbol):
        self.calls += 1
        return type(
            "Consensus",
            (),
            {
                "signal": "WAIT"
            }
        )()


class FakeIntelligenceFlow:
    def __init__(self):
        self.calls = 0
        self.enable_inline_outcome_learning = False

    def create_report(self, consensus):
        self.calls += 1

        proposal = type(
            "ActionProposal",
            (),
            {
                "action": "WAIT",
                "status": "REJECTED",
                "reason": "Monitoring",
            }
        )()

        return type(
            "Report",
            (),
            {
                "action_proposal": proposal,
                "decision": None,
                "signal": "WAIT",
                "trend": "NEUTRAL",
                "regime": "RANGING",
                "confidence": 70,
                "risk": "MEDIUM",
            }
        )()


def build_runner(tmp_path):
    exchange = FakeExchangeManager()
    pipeline = FakeMultiTimeframePipeline()
    intelligence = FakeIntelligenceFlow()
    session = PaperTradingSession()
    archive = PaperSessionArchive(
        tmp_path / "sessions"
    )

    runner = PaperMarketCycleRunner(
        exchange_manager=exchange,
        multi_timeframe_pipeline=pipeline,
        intelligence_flow=intelligence,
        session=session,
        session_archive=archive,
    )

    return runner, exchange, pipeline, intelligence


def test_runtime_checkpoint_restores_and_continues_from_next_cycle(tmp_path):
    runner, exchange, pipeline, intelligence = build_runner(tmp_path)

    first_results = runner.run(
        cycle_count=2,
        symbol="BTCUSDT"
    )

    assert len(first_results) == 2
    assert exchange.calls == [
        "BTCUSDT",
        "BTCUSDT",
    ]
    assert pipeline.calls == 2
    assert intelligence.calls == 2

    checkpoint = runner.build_runtime_checkpoint(
        completed_cycles=2
    )

    assert checkpoint["session_id"] == runner.session.session_id
    assert checkpoint["last_completed_cycle"] == 2
    assert checkpoint["symbol"] == "BTCUSDT"
    assert "session" in checkpoint

    restored_session = PaperTradingSession.from_checkpoint(
        checkpoint["session"]
    )

    restored_runner, restored_exchange, restored_pipeline, restored_intelligence = (
        build_runner(tmp_path)
    )

    restored_runner.session = restored_session

    second_results = restored_runner.run(
        cycle_count=1,
        symbol="BTCUSDT"
    )

    assert len(second_results) == 1
    assert restored_exchange.calls == [
        "BTCUSDT"
    ]
    assert restored_pipeline.calls == 1
    assert restored_intelligence.calls == 1

    assert (
        checkpoint["last_completed_cycle"]
        == 2
    )
