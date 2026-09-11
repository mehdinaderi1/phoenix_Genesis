from execution.paper_session_performance import PaperSessionPerformance


def test_analyze_profitable_session():
    analyzer = PaperSessionPerformance()

    session = {
        "cycles": [
            {"cycle": 1, "realized_pnl": 10.0},
            {"cycle": 2, "realized_pnl": -5.0},
            {"cycle": 3, "realized_pnl": 15.0}
        ],
        "summary": {
            "cycles_processed": 3,
            "trade_count": 3,
            "total_pnl": 20.0
        }
    }

    result = analyzer.analyze(session)

    assert result["cycles_processed"] == 3
    assert result["trade_count"] == 3
    assert result["win_count"] == 2
    assert result["loss_count"] == 1
    assert result["win_rate"] == 66.66666666666666
    assert result["total_pnl"] == 20.0
    assert result["average_pnl"] == 20.0 / 3


def test_analyze_losing_session():
    analyzer = PaperSessionPerformance()

    session = {
        "cycles": [
            {"cycle": 1, "realized_pnl": -10.0},
            {"cycle": 2, "realized_pnl": -5.0}
        ],
        "summary": {
            "cycles_processed": 2,
            "trade_count": 2,
            "total_pnl": -15.0
        }
    }

    result = analyzer.analyze(session)

    assert result["win_count"] == 0
    assert result["loss_count"] == 2
    assert result["win_rate"] == 0.0
    assert result["total_pnl"] == -15.0
    assert result["average_pnl"] == -7.5


def test_analyze_session_without_trades():
    analyzer = PaperSessionPerformance()

    session = {
        "cycles": [
            {"cycle": 1, "realized_pnl": None},
            {"cycle": 2, "realized_pnl": None}
        ],
        "summary": {
            "cycles_processed": 2,
            "trade_count": 0,
            "total_pnl": 0.0
        }
    }

    result = analyzer.analyze(session)

    assert result["trade_count"] == 0
    assert result["win_count"] == 0
    assert result["loss_count"] == 0
    assert result["win_rate"] == 0.0
    assert result["average_pnl"] == 0.0


def test_analyze_ignores_unrealized_cycles():
    analyzer = PaperSessionPerformance()

    session = {
        "cycles": [
            {"cycle": 1, "realized_pnl": None},
            {"cycle": 2, "realized_pnl": 25.0}
        ],
        "summary": {
            "cycles_processed": 2,
            "trade_count": 1,
            "total_pnl": 25.0
        }
    }

    result = analyzer.analyze(session)

    assert result["cycles_processed"] == 2
    assert result["trade_count"] == 1
    assert result["win_count"] == 1
    assert result["loss_count"] == 0
    assert result["win_rate"] == 100.0
    assert result["total_pnl"] == 25.0
    assert result["average_pnl"] == 25.0
