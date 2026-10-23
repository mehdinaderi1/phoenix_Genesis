"""
Test LivePositionTracker + Reconciliation.
Uses a fake execution result — no real orders placed.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from execution.live.position_tracker import LivePositionTracker
from execution.live.reconciliation import LiveReconciler
from execution.live.order_executor import ExecutionResult
from execution.live.order_state_machine import OrderStatus


class FakeExec:
    def __init__(self, success=True, order_id="test-1",
                 filled_qty=0.00013, avg_price=80000.0):
        self.success = success
        self.order_id = order_id
        self.status = OrderStatus.FILLED if success else OrderStatus.REJECTED
        self.filled_quantity = filled_qty
        self.avg_fill_price = avg_price
        self.total_cost = filled_qty * avg_price
        self.raw_snapshot = None
        self.error = None


def main():
    print("=" * 60)
    print("Testing LivePositionTracker")
    print("=" * 60)
    print()

    tracker = LivePositionTracker()

    # Simulate: BUY 0.00013 BTC @ 80000
    buy = FakeExec(order_id="buy-1", filled_qty=0.00013, avg_price=80000)
    pos = tracker.open_from_fill(
        symbol="btc_usdt", side="BUY", execution_result=buy,
        sl=79000, tp=82000, fee_pct=0.0006,
    )
    print(f"1. Open: {pos}")
    print(f"   unrealized @ 81000: {pos.unrealized_pnl(81000):+.6f} USDT")
    print(f"   unrealized @ 81000: {pos.unrealized_pnl_pct(81000):+.2f}%")
    print()

    # Serialization
    d = tracker.to_dict()
    print(f"2. Serialized: {d}")
    print()

    # Simulate close
    sell = FakeExec(order_id="sell-1", filled_qty=0.00013, avg_price=81000)
    result = tracker.close_from_fill("btc_usdt", sell)
    print(f"3. Close: {result}")
    print()
    print(f"   Position still open? {tracker.has_position('btc_usdt')}")
    print()

    # Reconciliation (mock)
    class FakeExchange:
        def fetch_balances(self):
            return []  # empty, but we have no position either
    reconciler = LiveReconciler(FakeExchange())
    r = reconciler.reconcile(tracker)
    print(f"4. Reconcile: {r}")
    print(f"   clean: {r.clean}")
    print()
    print(">>> TRACKER OK <<<")


if __name__ == "__main__":
    main()