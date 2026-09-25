import main


class FakeObservation:
    def __init__(self, status="HEALTHY"):
        self.price = 65012.34
        self.source = "coinmarketcap"
        self.source_status = status


class FakeDecision:
    def __init__(self, action="WAIT"):
        self.action = action


class FakePaperResult(dict):
    def __init__(self):
        super().__init__(action="HOLD", realized_pnl=0)


def test_print_cycle_handles_missing_market_context(capsys):
    result = {
        "cycle_number": 1,
        "observation": FakeObservation(),
        "market_context": None,
        "decision": None,
        "action_proposal": None,
        "translated_action_proposal": None,
        "paper_result": None,
    }

    main.print_cycle(result)

    output = capsys.readouterr().out

    assert "Cycle 1" in output
    assert "Price=65012.34" in output
    assert "Source=coinmarketcap" in output
    assert "Status=HEALTHY" in output
    assert "Market Context=None" in output
    assert "Intelligence=SKIPPED" in output
    assert "Paper=SKIPPED" in output


def test_print_cycle_handles_blind_observation(capsys):
    result = {
        "cycle_number": 2,
        "observation": FakeObservation(status="BLIND"),
        "market_context": None,
        "decision": None,
        "action_proposal": None,
        "translated_action_proposal": None,
        "paper_result": None,
    }

    main.print_cycle(result)

    output = capsys.readouterr().out

    assert "Cycle 2" in output
    assert "Price=None" in output
    assert "Source=None" in output
    assert "Status=BLIND" in output


def test_print_cycle_shows_decision_gate_visibility(capsys):
    result = {
        "cycle_number": 3,
        "observation": FakeObservation(),
        "market_context": type("Context", (), {
            "trend": "BULLISH",
            "signal": "BUY",
            "confidence": 70.0,
        })(),
        "decision": FakeDecision("WAIT"),
        "action_proposal": None,
        "translated_action_proposal": None,
        "paper_result": FakePaperResult(),
    }

    main.print_cycle(result)

    output = capsys.readouterr().out

    assert "Decision=WAIT" in output
    assert "LongGate=BLOCKED" in output


def test_print_cycle_shows_operational_strategy(capsys):
    result = {
        "cycle_number": 4,
        "observation": FakeObservation(),
        "market_context": type("Context", (), {
            "trend": "BEARISH",
            "signal": "WAIT",
            "confidence": 17.5,
        })(),
        "report": type("Report", (), {
            "signal": "WAIT",
            "risk": "HIGH",
            "confidence": 17.5,
            "regime": "BEARISH",
            "strategy_ranking": None,
            "champion_strategy": None,
            "operational_strategy_result": {
                "strategy": "BTC_MTF_TREND_ALIGNMENT_V1",
                "signal": "WAIT",
                "direction": None,
                "matched": False,
            }
        })(),
        "decision": FakeDecision("WAIT"),
        "action_proposal": None,
        "translated_action_proposal": None,
        "paper_result": FakePaperResult(),
    }

    main.print_cycle(result)

    output = capsys.readouterr().out

    assert "Strategy=BTC_MTF_TREND_ALIGNMENT_V1" in output
