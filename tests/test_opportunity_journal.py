import json

from intelligence.observation.opportunity_journal import OpportunityJournal


def test_journal_appends_records_and_preserves_previous_entries(tmp_path):
    journal_path = tmp_path / "opportunities.jsonl"
    journal = OpportunityJournal(journal_path)

    first = {
        "symbol": "BTCUSDT",
        "signal": "BUY",
        "reference_price": 65000.0,
        "execution_attempted": False,
    }
    second = {
        "symbol": "BTCUSDT",
        "signal": "SELL",
        "reference_price": 65500.0,
        "execution_attempted": False,
    }

    journal.append(first)
    journal.append(second)

    lines = journal_path.read_text(encoding="utf-8").splitlines()
    records = [json.loads(line) for line in lines]

    assert records == [first, second]
    assert journal.read_all() == [first, second]
