from core.market_data.operational_action_translator import (
    OperationalActionTranslator,
)
from intelligence.action_proposal import ActionProposal
from intelligence.decision_validator import DecisionValidator


def test_action_proposal_validation_matrix():
    validator = DecisionValidator()

    wait = ActionProposal(
        action="WAIT",
        status="PENDING",
        reason="No valid action",
        confidence=85,
    )

    long_action = ActionProposal(
        action="PREPARE_LONG",
        status="PENDING",
        reason="Strong bullish setup",
        confidence=85,
    )

    short_action = ActionProposal(
        action="PREPARE_SHORT",
        status="PENDING",
        reason="Strong bearish setup",
        confidence=75,
    )

    assert validator.validate(wait) is False
    assert validator.validate(long_action) is True
    assert validator.validate(short_action) is True


def test_action_proposal_translation():
    translator = OperationalActionTranslator()

    long_proposal = ActionProposal(
        action="PREPARE_LONG",
        status="APPROVED",
        reason="Strong bullish setup",
        confidence=85,
        risk_status="LOW",
    )

    short_proposal = ActionProposal(
        action="PREPARE_SHORT",
        status="APPROVED",
        reason="Strong bearish setup",
        confidence=75,
        risk_status="MEDIUM",
    )

    wait_proposal = ActionProposal(
        action="WAIT",
        status="REJECTED",
        reason="No valid action",
        confidence=40,
        risk_status="HIGH",
    )

    translated_long = translator.translate(long_proposal)
    translated_short = translator.translate(short_proposal)
    translated_wait = translator.translate(wait_proposal)

    assert translated_long.action == "BUY"
    assert translated_long.status == "APPROVED"
    assert translated_long.metadata["translated_from"] == "PREPARE_LONG"

    assert translated_short.action == "SELL"
    assert translated_short.status == "APPROVED"
    assert translated_short.metadata["translated_from"] == "PREPARE_SHORT"

    assert translated_wait.action == "WAIT"
    assert translated_wait.status == "REJECTED"
    assert translated_wait.risk_status == "HIGH"


def test_translated_action_preserves_decision_context():
    translator = OperationalActionTranslator()

    proposal = ActionProposal(
        action="PREPARE_LONG",
        status="APPROVED",
        reason="Strong bullish setup",
        confidence=85,
        symbol="BTCUSDT",
        strategy="momentum_strategy",
        risk_status="LOW",
        metadata={"source": "decision_engine"},
    )

    translated = translator.translate(proposal)

    assert translated.action == "BUY"
    assert translated.status == "APPROVED"
    assert translated.reason == "Strong bullish setup"
    assert translated.confidence == 85
    assert translated.symbol == "BTCUSDT"
    assert translated.strategy == "momentum_strategy"
    assert translated.risk_status == "LOW"
    assert translated.metadata["source"] == "decision_engine"
    assert translated.metadata["translated_from"] == "PREPARE_LONG"
