from execution.xt_futures_prepared_execution_runtime import (
    XTFuturesPreparedExecutionRuntime,
)
from intelligence.action_proposal import ActionProposal


def test_prepared_execution_runtime_builds_xt_order():
    runtime = XTFuturesPreparedExecutionRuntime(
        balance=1000.0,
        position_size_percent=1.0,
    )

    proposal = ActionProposal(
        action="BUY",
        status="APPROVED",
        symbol="BTCUSDT",
        confidence=90,
        reason="approved runtime test",
    )

    results = runtime.run(
        cycles=[
            {
                "action_proposal": proposal,
                "price": 50000.0,
            }
        ],
        symbol="BTCUSDT",
    )

    assert len(results) == 1

    result = results[0]

    assert result["status"] == "PREPARED"
    assert result["request"].symbol == "BTCUSDT"
    assert result["request"].order_side == "BUY"
    assert result["request"].position_side == "LONG"
    assert result["request"].quantity == 0.0002

    assert result["payload"] == {
        "symbol": "BTCUSDT",
        "orderSide": "BUY",
        "positionSide": "LONG",
        "orderType": "MARKET",
        "origQty": 0.0002,
    }


def test_prepared_execution_runtime_does_not_prepare_rejected_action():
    runtime = XTFuturesPreparedExecutionRuntime(
        balance=1000.0,
        position_size_percent=1.0,
    )

    proposal = ActionProposal(
        action="BUY",
        status="REJECTED",
        symbol="BTCUSDT",
        confidence=90,
    )

    results = runtime.run(
        cycles=[
            {
                "action_proposal": proposal,
                "price": 50000.0,
            }
        ],
        symbol="BTCUSDT",
    )

    assert len(results) == 1
    assert results[0]["status"] == "NOT_PREPARED"
    assert results[0]["prepared"] is None


def test_prepared_execution_runtime_does_not_send_network_requests():
    runtime = XTFuturesPreparedExecutionRuntime(
        balance=1000.0,
        position_size_percent=1.0,
    )

    proposal = ActionProposal(
        action="SELL",
        status="APPROVED",
        symbol="BTCUSDT",
        confidence=90,
    )

    results = runtime.run(
        cycles=[
            {
                "action_proposal": proposal,
                "price": 50000.0,
            }
        ],
        symbol="BTCUSDT",
    )

    assert results[0]["status"] == "PREPARED"
    assert results[0]["execution"] is None
