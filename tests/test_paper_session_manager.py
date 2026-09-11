from execution.paper_session_archive import PaperSessionArchive
from execution.paper_session_manager import PaperSessionManager


class FakeArchive:

    def __init__(self):
        self.sessions = {
            "session_002": {
                "cycles": [],
                "summary": {
                    "cycles_processed": 2,
                    "balance": 1001.0,
                    "total_pnl": 1.0
                },
                "final_position": None
            },
            "session_001": {
                "cycles": [],
                "summary": {
                    "cycles_processed": 3,
                    "balance": 1000.0,
                    "total_pnl": 0.0
                },
                "final_position": None
            }
        }

    def list(self):
        return sorted(self.sessions.keys())

    def load(self, session_id):
        return self.sessions[session_id]


def test_list_sessions():
    archive = FakeArchive()
    manager = PaperSessionManager(archive)

    sessions = manager.list_sessions()

    assert sessions == [
        "session_001",
        "session_002"
    ]


def test_get_session():
    archive = FakeArchive()
    manager = PaperSessionManager(archive)

    session = manager.get_session("session_001")

    assert session["summary"]["cycles_processed"] == 3
    assert session["summary"]["balance"] == 1000.0


def test_get_session_summary():
    archive = FakeArchive()
    manager = PaperSessionManager(archive)

    summary = manager.get_session_summary("session_002")

    assert summary == {
        "cycles_processed": 2,
        "balance": 1001.0,
        "total_pnl": 1.0
    }


def test_manager_uses_archive_for_session_loading():
    archive = FakeArchive()
    manager = PaperSessionManager(archive)

    session = manager.get_session("session_002")

    assert session["final_position"] is None
    assert session["cycles"] == []


def test_manager_integrates_with_real_archive(tmp_path):
    archive = PaperSessionArchive(tmp_path)

    session_record = {
        "cycles": [
            {
                "cycle": 1,
                "action": "HOLD"
            },
            {
                "cycle": 2,
                "action": "HOLD"
            }
        ],
        "summary": {
            "cycles_processed": 2,
            "balance": 1000.0,
            "total_pnl": 0.0
        },
        "final_position": None
    }

    archive.save(
        "session_integration",
        session_record
    )

    manager = PaperSessionManager(
        archive
    )

    sessions = manager.list_sessions()
    loaded_session = manager.get_session(
        "session_integration"
    )
    summary = manager.get_session_summary(
        "session_integration"
    )

    assert sessions == [
        "session_integration"
    ]

    assert loaded_session == session_record

    assert summary == {
        "cycles_processed": 2,
        "balance": 1000.0,
        "total_pnl": 0.0
    }

def test_get_session_performance():
    archive = FakeArchive()

    archive.sessions["session_002"]["cycles"] = [
        {"cycle": 1, "realized_pnl": 10.0},
        {"cycle": 2, "realized_pnl": -5.0},
        {"cycle": 3, "realized_pnl": 15.0}
    ]

    archive.sessions["session_002"]["summary"]["cycles_processed"] = 3
    archive.sessions["session_002"]["summary"]["trade_count"] = 3
    archive.sessions["session_002"]["summary"]["total_pnl"] = 20.0

    manager = PaperSessionManager(archive)

    performance = manager.get_session_performance(
        "session_002"
    )

    assert performance["cycles_processed"] == 3
    assert performance["trade_count"] == 3
    assert performance["win_count"] == 2
    assert performance["loss_count"] == 1
    assert performance["win_rate"] == 2 / 3 * 100
    assert performance["total_pnl"] == 20.0
    assert performance["average_pnl"] == 20.0 / 3

def test_manager_get_session_performance_from_real_archive(tmp_path):
    archive = PaperSessionArchive(tmp_path)

    session_record = {
        "cycles": [
            {
                "cycle": 1,
                "action": "OPEN",
                "realized_pnl": None
            },
            {
                "cycle": 2,
                "action": "CLOSE",
                "realized_pnl": 25.0
            },
            {
                "cycle": 3,
                "action": "CLOSE",
                "realized_pnl": -10.0
            }
        ],
        "summary": {
            "cycles_processed": 3,
            "trade_count": 2,
            "total_pnl": 15.0
        },
        "final_position": None
    }

    archive.save(
        "session_performance_integration",
        session_record
    )

    manager = PaperSessionManager(
        archive
    )

    performance = manager.get_session_performance(
        "session_performance_integration"
    )

    assert performance["cycles_processed"] == 3
    assert performance["trade_count"] == 2
    assert performance["win_count"] == 1
    assert performance["loss_count"] == 1
    assert performance["win_rate"] == 50.0
    assert performance["total_pnl"] == 15.0
    assert performance["average_pnl"] == 7.5


def test_get_session_report():
    archive = FakeArchive()

    archive.sessions["session_002"]["cycles"] = [
        {"cycle": 1, "realized_pnl": 10.0},
        {"cycle": 2, "realized_pnl": -5.0},
        {"cycle": 3, "realized_pnl": 15.0}
    ]

    archive.sessions["session_002"]["summary"]["cycles_processed"] = 3
    archive.sessions["session_002"]["summary"]["trade_count"] = 3
    archive.sessions["session_002"]["summary"]["total_pnl"] = 20.0

    manager = PaperSessionManager(
        archive
    )

    report = manager.get_session_report(
        "session_002"
    )

    assert report["session_id"] == "session_002"
    assert report["cycles"] == 3
    assert report["trade_count"] == 3
    assert report["win_count"] == 2
    assert report["loss_count"] == 1
    assert report["win_rate"] == (
        2 / 3 * 100
    )
    assert report["total_pnl"] == 20.0
    assert report["average_pnl"] == (
        20.0 / 3
    )
