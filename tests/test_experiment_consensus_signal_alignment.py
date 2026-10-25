from intelligence.decision_rules import DecisionRules


class Report:
    def __init__(self, signal, consensus):
        self.signal = signal
        self.strategy_consensus = consensus


def make_consensus(decision):
    return {
        "decision": decision,
        "supporting_strategies": 3,
        "opposing_strategies": 1,
        "confidence": 0.85,
    }


def test_wait_report_with_sell_strategy_consensus_is_invalid():
    report = Report(
        signal="WAIT",
        consensus=make_consensus("SELL"),
    )

    assert DecisionRules().consensus_is_valid(report) is False


def test_sell_report_with_sell_strategy_consensus_is_valid():
    report = Report(
        signal="SELL",
        consensus=make_consensus("SELL"),
    )

    assert DecisionRules().consensus_is_valid(report) is True
