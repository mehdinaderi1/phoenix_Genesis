from execution.paper_market_cycle_runner import PaperMarketCycleRunner
from execution.paper_session_archive import PaperSessionArchive
from execution.paper_trading_session import PaperTradingSession


class FakeExchangeManager:
    def get_price(self, symbol):
        return 65000.0


class FakeMultiTimeframePipeline:
    def analyze(self, symbol):
        return type(
            "Consensus",
            (),
            {"signal": "WAIT"}
        )()


class FakeIntelligenceFlow:
    enable_inline_outcome_learning = False

    def create_report(self, consensus):
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


def build_runner(tmp_path):
    return PaperMarketCycleRunner(
        exchange_manager=FakeExchangeManager(),
        multi_timeframe_pipeline=FakeMultiTimeframePipeline(),
        intelligence_flow=FakeIntelligenceFlow(),
        session=PaperTradingSession(),
        session_archive=PaperSessionArchive(
            tmp_path / "sessions"
        )
    )


def test_runtime_checkpoint_can_be_saved_and_loaded(tmp_path):
    runner = build_runner(tmp_path)

    checkpoint = runner.build_runtime_checkpoint(
        completed_cycles=2,
        symbol="BTCUSDT"
    )

    runner.save_runtime_checkpoint(checkpoint)

    restored = runner.load_runtime_checkpoint()

    assert restored["session_id"] == runner.session.session_id
    assert restored["last_completed_cycle"] == 2
    assert restored["symbol"] == "BTCUSDT"
    assert restored["session"]["session_id"] == (
        runner.session.session_id
    )
