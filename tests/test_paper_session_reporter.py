from execution.paper_session_archive import PaperSessionArchive
from execution.paper_session_performance import PaperSessionPerformance
from execution.paper_session_reporter import PaperSessionReporter


def test_build_report_from_real_archive(tmp_path):
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
                "realized_pnl": 30.0
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
            "total_pnl": 20.0
        },
        "final_position": None
    }

    archive.save(
        "session_report_integration",
        session_record
    )

    session = archive.load(
        "session_report_integration"
    )

    performance = PaperSessionPerformance().analyze(
        session
    )

    report = PaperSessionReporter().build_report(
        "session_report_integration",
        session,
        performance
    )

    assert report["session_id"] == "session_report_integration"
    assert report["cycles"] == 3
    assert report["trade_count"] == 2
    assert report["win_count"] == 1
    assert report["loss_count"] == 1
    assert report["win_rate"] == 50.0
    assert report["total_pnl"] == 20.0
    assert report["average_pnl"] == 10.0
    assert report["final_position"] is None
