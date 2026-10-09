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
            {"signal": "WAIT"}
        )()


class FakeIntelligenceFlow:
    enable_inline_outcome_learning = False

    def __init__(self):
        self.calls = 0

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
                "trend": "NEUTRAL",
                "regime": "RANGING",
                "confidence": 70,
                "risk": "MEDIUM",
            }
        )()


def build_runner(tmp_path, session=None):
    exchange = FakeExchangeManager()
    pipeline = FakeMultiTimeframePipeline()
    intelligence = FakeIntelligenceFlow()

    runner = PaperMarketCycleRunner(
        exchange_manager=exchange,
        multi_timeframe_pipeline=pipeline,
        intelligence_flow=intelligence,
        session=session or PaperTradingSession(),
        session_archive=PaperSessionArchive(
            tmp_path / "sessions"
        )
    )

    return runner, exchange, pipeline, intelligence


def test_runtime_checkpoint_is_saved_after_each_completed_cycle_and_resume_starts_next_cycle(
    tmp_path
):
    runner_a, exchange_a, pipeline_a, intelligence_a = build_runner(
        tmp_path
    )

    results = runner_a.run(
        cycle_count=2,
        symbol="BTCUSDT"
    )

    assert len(results) == 2
    assert len(exchange_a.calls) == 2
    assert pipeline_a.calls == 2
    assert intelligence_a.calls == 2

    checkpoint = runner_a.load_runtime_checkpoint()

    assert checkpoint["last_completed_cycle"] == 2
    assert checkpoint["symbol"] == "BTCUSDT"

    runner_b, exchange_b, pipeline_b, intelligence_b = build_runner(
        tmp_path
    )

    restored = runner_b.restore_runtime_checkpoint()

    assert restored["last_completed_cycle"] == 2
    assert runner_b.session.session_id == runner_a.session.session_id

    next_results = runner_b.run(
        cycle_count=1,
        symbol="BTCUSDT"
    )

    assert len(next_results) == 1
    assert exchange_b.calls == ["BTCUSDT"]
    assert pipeline_b.calls == 1
    assert intelligence_b.calls == 1

    resumed_checkpoint = runner_b.load_runtime_checkpoint()

    assert resumed_checkpoint["last_completed_cycle"] == 3
