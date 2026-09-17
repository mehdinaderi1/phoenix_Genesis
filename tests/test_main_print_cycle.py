import main


class FakeObservation:
    def __init__(self, status="HEALTHY"):
        self.price = 65012.34
        self.source = "coinmarketcap"
        self.source_status = status


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
    assert "Market Context=None" in output
    assert "Intelligence=SKIPPED" in output
    assert "Paper=SKIPPED" in output
