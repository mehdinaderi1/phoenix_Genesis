from intelligence.decision_rules import DecisionRules


class Report:

    def __init__(
        self,
        consensus
    ):
        self.strategy_consensus = consensus



def test_consensus_allows_high_confidence_majority():

    rules = DecisionRules()

    report = Report(
        {
            "decision": "BUY",
            "supporting_strategies": 3,
            "opposing_strategies": 1,
            "confidence": 0.85
        }
    )


    assert (
        rules.consensus_is_valid(report)
        is True
    )



def test_consensus_blocks_low_confidence_majority():

    rules = DecisionRules()

    report = Report(
        {
            "decision": "BUY",
            "supporting_strategies": 3,
            "opposing_strategies": 1,
            "confidence": 0.40
        }
    )


    assert (
        rules.consensus_is_valid(report)
        is False
    )



def test_consensus_blocks_equal_vote():

    rules = DecisionRules()

    report = Report(
        {
            "decision": "BUY",
            "supporting_strategies": 2,
            "opposing_strategies": 2,
            "confidence": 0.90
        }
    )


    assert (
        rules.consensus_is_valid(report)
        is False
    )