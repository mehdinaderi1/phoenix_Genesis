import json
from types import SimpleNamespace

from execution.paper_market_cycle_runner import (
    PaperMarketCycleRunner
)
from execution.paper_session_serializer import (
    PaperSessionSerializer
)
from execution.paper_trading_session import (
    PaperTradingSession
)


class FakeExchangeManager:

    def __init__(self):
        self.calls = 0

    def get_price(self, symbol):
        self.calls += 1
        return 65000.0


class FakeMultiTimeframePipeline:

    def __init__(self):
        self.calls = 0

    def analyze(self, symbol):
        self.calls += 1
        return SimpleNamespace(
            signal="BUY"
        )


class FakeIntelligenceFlow:

    def __init__(self):
        self.calls = 0

    def create_report(self, consensus):
        self.calls += 1

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


def test_serializes_session_record_to_json():
    serializer = PaperSessionSerializer()

    session_record = {
        "cycles": [
            {
                "cycle": 1,
                "symbol": "BTCUSDT",
                "price": 65000.0,
                "action": "OPEN",
                "realized_pnl": 0.0
            }
        ],
        "summary": {
            "cycles_processed": 1,
            "open_count": 1,
            "hold_count": 0,
            "close_count": 0,
            "balance": 1000.0,
            "total_pnl": 0.0,
            "trade_count": 0
        },
        "final_position": None
    }

    serialized = serializer.serialize(
        session_record
    )

    assert isinstance(
        serialized,
        str
    )

    restored = json.loads(
        serialized
    )

    assert restored == session_record


def test_serializes_empty_session_record():
    serializer = PaperSessionSerializer()

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

    serialized = serializer.serialize(
        session_record
    )

    assert json.loads(
        serialized
    ) == session_record


def test_serializes_real_runner_session_record():
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

    serializer = PaperSessionSerializer()

    serialized = serializer.serialize(
        session_record
    )

    restored = json.loads(
        serialized
    )

    assert restored["summary"]["cycles_processed"] == 3
    assert restored["summary"]["hold_count"] == 3
    assert restored["summary"]["open_count"] == 0
    assert restored["summary"]["close_count"] == 0

    assert restored["summary"]["balance"] == 1000.0
    assert restored["summary"]["total_pnl"] == 0.0
    assert restored["summary"]["trade_count"] == 0

    assert restored["final_position"] is None

    assert len(
        restored["cycles"]
    ) == 3

    assert restored["cycles"][0]["cycle"] == 1
    assert restored["cycles"][0]["symbol"] == "BTCUSDT"
    assert restored["cycles"][0]["price"] == 65000.0
    assert restored["cycles"][0]["action"] == "HOLD"

    assert all(
        cycle["action"] == "HOLD"
        for cycle in restored["cycles"]
    )