from intelligence.decision_validator import DecisionValidator
from intelligence.decision import DecisionResult


def test_valid_decision():

    decision = DecisionResult(
        action="PREPARE_LONG",
        reason="Strong bullish signal",
        confidence=85
    )

    validator = DecisionValidator()

    result = validator.validate(decision)

    assert result is True


def test_wait_decision():

    decision = DecisionResult(
        action="WAIT",
        reason="No confirmation",
        confidence=50
    )

    validator = DecisionValidator()

    result = validator.validate(decision)

    assert result is False