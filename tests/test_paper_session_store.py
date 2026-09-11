from execution.paper_session_store import (
    PaperSessionStore
)

from types import SimpleNamespace

from execution.paper_market_cycle_runner import (
    PaperMarketCycleRunner
)
from execution.paper_trading_session import (
    PaperTradingSession
)

from execution.paper_session_store import (
    PaperSessionStore
)


def test_saves_session_record_to_file(
    tmp_path
):
    store = PaperSessionStore()

    session_record = {
        "cycles": [],
        "summary": {
            "cycles_processed": 0,
            "open_count": 0,
            "hold_count": 0,
            "close_count": 0,
            "balance": 1000.0,
            "total_pnl": 0.0,
            "trade_count": 0
        },
        "final_position": None
    }

    path = tmp_path / "session.json"

    store.save(
        session_record,
        path
    )

    assert path.exists()


def test_loads_session_record_from_file(
    tmp_path
):
    store = PaperSessionStore()

    session_record = {
        "cycles": [
            {
                "cycle": 1,
                "symbol": "BTCUSDT",
                "price": 65000.0,
                "action": "HOLD",
                "realized_pnl": 0.0
            }
        ],
        "summary": {
            "cycles_processed": 1,
            "open_count": 0,
            "hold_count": 1,
            "close_count": 0,
            "balance": 1000.0,
            "total_pnl": 0.0,
            "trade_count": 0
        },
        "final_position": None
    }

    path = tmp_path / "session.json"

    store.save(
        session_record,
        path
    )

    restored = store.load(
        path
    )

    assert restored == session_record


def test_session_store_round_trip(
    tmp_path
):
    store = PaperSessionStore()

    session_record = {
        "cycles": [
            {
                "cycle": 1,
                "symbol": "BTCUSDT",
                "price": 65000.0,
                "action": "OPEN",
                "realized_pnl": 0.0
            },
            {
                "cycle": 2,
                "symbol": "BTCUSDT",
                "price": 65500.0,
                "action": "HOLD",
                "realized_pnl": 0.0
            },
            {
                "cycle": 3,
                "symbol": "BTCUSDT",
                "price": 66000.0,
                "action": "CLOSE",
                "realized_pnl": 1.5384615384615385
            }
        ],
        "summary": {
            "cycles_processed": 3,
            "open_count": 1,
            "hold_count": 1,
            "close_count": 1,
            "balance": 1001.5384615384615,
            "total_pnl": 1.5384615384615472,
            "trade_count": 1
        },
        "final_position": None
    }

    path = tmp_path / "session.json"

    store.save(
        session_record,
        path
    )

    restored = store.load(
        path
    )

    assert restored == session_record


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


def test_runner_session_record_survives_file_persistence(
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

    store = PaperSessionStore()

    path = tmp_path / "paper_session.json"

    store.save(
        session_record,
        path
    )

    restored = store.load(
        path
    )

    assert restored == session_record

    assert restored["summary"]["cycles_processed"] == 3
    assert restored["summary"]["hold_count"] == 3
    assert restored["summary"]["balance"] == 1000.0
    assert restored["summary"]["total_pnl"] == 0.0
    assert restored["final_position"] is None

    assert len(
        restored["cycles"]
    ) == 3