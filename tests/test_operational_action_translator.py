from types import SimpleNamespace

from core.market_data.operational_action_translator import (
    OperationalActionTranslator
)


def test_translates_prepare_long_to_buy():
    proposal = SimpleNamespace(
        action="PREPARE_LONG",
        status="APPROVED",
        reason="long",
        confidence=85.0,
        symbol=None,
        strategy=None,
        risk_status="UNKNOWN",
        metadata={}
    )

    result = OperationalActionTranslator().translate(proposal)

    assert result.action == "BUY"
    assert result.status == "APPROVED"
    assert result.confidence == 85.0
    assert result.metadata["translated_from"] == "PREPARE_LONG"


def test_translates_prepare_short_to_sell():
    proposal = SimpleNamespace(
        action="PREPARE_SHORT",
        status="APPROVED",
        reason="short",
        confidence=80.0,
        symbol=None,
        strategy=None,
        risk_status="UNKNOWN",
        metadata={}
    )

    result = OperationalActionTranslator().translate(proposal)

    assert result.action == "SELL"
    assert result.metadata["translated_from"] == "PREPARE_SHORT"


def test_keeps_wait_unchanged():
    proposal = SimpleNamespace(
        action="WAIT",
        status="REJECTED",
        reason="wait",
        confidence=50.0,
        metadata={}
    )

    result = OperationalActionTranslator().translate(proposal)

    assert result is proposal


def test_keeps_unknown_action_unchanged():
    proposal = SimpleNamespace(
        action="HOLD",
        status="APPROVED",
        reason="hold",
        confidence=50.0,
        metadata={}
    )

    result = OperationalActionTranslator().translate(proposal)

    assert result is proposal


def test_rejects_none():
    try:
        OperationalActionTranslator().translate(None)
        assert False
    except ValueError as exc:
        assert str(exc) == "action_proposal must not be None"

def test_translates_prepare_short_to_sell():
    proposal = SimpleNamespace(
        action="PREPARE_SHORT",
        status="APPROVED",
        reason="short",
        confidence=80.0,
        symbol=None,
        strategy=None,
        risk_status="UNKNOWN",
        metadata={}
    )

    result = OperationalActionTranslator().translate(proposal)

    assert result.action == "SELL"
    assert result.metadata["translated_from"] == "PREPARE_SHORT"
