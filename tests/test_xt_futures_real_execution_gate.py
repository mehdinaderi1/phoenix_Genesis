import pytest

from execution.xt_futures_real_execution_gate import (
    XTFuturesRealExecutionGate,
)


def test_real_execution_is_blocked_by_default():
    gate = XTFuturesRealExecutionGate(
        demo_mode=True,
    )

    assert gate.is_authorized is False

    with pytest.raises(PermissionError):
        gate.authorize()


def test_demo_mode_blocks_real_execution_even_when_enabled():
    gate = XTFuturesRealExecutionGate(
        demo_mode=True,
        real_execution_enabled=True,
    )

    assert gate.is_authorized is False

    with pytest.raises(PermissionError):
        gate.authorize()


def test_real_execution_requires_explicit_enablement():
    gate = XTFuturesRealExecutionGate(
        demo_mode=False,
        real_execution_enabled=False,
    )

    assert gate.is_authorized is False

    with pytest.raises(PermissionError):
        gate.authorize()


def test_real_execution_requires_both_conditions():
    gate = XTFuturesRealExecutionGate(
        demo_mode=False,
        real_execution_enabled=True,
    )

    assert gate.is_authorized is True
    assert gate.authorize() is True
