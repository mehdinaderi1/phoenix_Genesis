from execution.paper_session_archive import (
    PaperSessionArchive
)

from execution.paper_session_archive import (
    PaperSessionArchive
)


def build_session_record(
    session_number
):
    return {
        "cycles": [],
        "summary": {
            "cycles_processed": session_number,
            "open_count": 0,
            "hold_count": session_number,
            "close_count": 0,
            "balance": 1000.0,
            "total_pnl": 0.0,
            "trade_count": 0
        },
        "final_position": None
    }


def test_saves_session_to_archive(
    tmp_path
):
    archive = PaperSessionArchive(
        tmp_path
    )

    session_record = build_session_record(
        1
    )

    archive.save(
        "session_001",
        session_record
    )

    assert (
        tmp_path / "session_001.json"
    ).exists()


def test_lists_saved_sessions(
    tmp_path
):
    archive = PaperSessionArchive(
        tmp_path
    )

    archive.save(
        "session_002",
        build_session_record(2)
    )

    archive.save(
        "session_001",
        build_session_record(1)
    )

    archive.save(
        "session_003",
        build_session_record(3)
    )

    assert archive.list() == [
        "session_001",
        "session_002",
        "session_003"
    ]


def test_loads_session_from_archive(
    tmp_path
):
    archive = PaperSessionArchive(
        tmp_path
    )

    session_record = build_session_record(
        3
    )

    archive.save(
        "session_003",
        session_record
    )

    restored = archive.load(
        "session_003"
    )

    assert restored == session_record


def test_archive_supports_multiple_sessions(
    tmp_path
):
    archive = PaperSessionArchive(
        tmp_path
    )

    session_one = build_session_record(
        1
    )

    session_two = build_session_record(
        2
    )

    archive.save(
        "session_001",
        session_one
    )

    archive.save(
        "session_002",
        session_two
    )

    assert archive.load(
        "session_001"
    ) == session_one

    assert archive.load(
        "session_002"
    ) == session_two

    assert archive.list() == [
        "session_001",
        "session_002"
    ]

from types import SimpleNamespace

from execution.paper_market_cycle_runner import (
    PaperMarketCycleRunner
)
from execution.paper_trading_session import (
    PaperTradingSession
)


class FakeExchangeManager:

    def get_price(self, symbol):
        return 65000.0


class FakeMultiTimeframePipeline:

    def analyze(self, symbol):
        return SimpleNamespace(
            signal="BUY"
        )


class FakeIntelligenceFlow:

    def create_report(self, consensus):
        proposal = SimpleNamespace(
            action="WAIT",
            status="REJECTED",
            reason="Monitoring",
            symbol="BTCUSDT"
        )

        return SimpleNamespace(
            symbol="BTCUSDT",
            timeframe="30m",
            trend="BULLISH",
            regime="RANGING",
            signal="BUY",
            confidence=70,
            risk="MEDIUM",
            reasons=["Monitoring"],
            action_proposal=proposal
        )


def test_runner_session_survives_archive_persistence(
    tmp_path
):
    session = PaperTradingSession(
        initial_balance=1000.0,
        position_size_percent=10.0
    )

    runner = PaperMarketCycleRunner(
        exchange_manager=FakeExchangeManager(),
        multi_timeframe_pipeline=(
            FakeMultiTimeframePipeline()
        ),
        intelligence_flow=FakeIntelligenceFlow(),
        session=session
    )

    results = runner.run(
        cycle_count=3,
        symbol="BTCUSDT"
    )

    session_record = runner.build_session_record(
        results
    )

    archive = PaperSessionArchive(
        tmp_path
    )

    archive.save(
        "session_001",
        session_record
    )

    restored = archive.load(
        "session_001"
    )

    assert restored == session_record

    assert restored["summary"]["cycles_processed"] == 3
    assert restored["summary"]["hold_count"] == 3
    assert restored["summary"]["balance"] == 1000.0
    assert restored["summary"]["total_pnl"] == 0.0

    assert len(
        restored["cycles"]
    ) == 3