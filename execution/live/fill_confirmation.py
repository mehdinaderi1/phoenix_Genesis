"""
Fill confirmation — poll exchange until order reaches terminal state.
"""
import time
from typing import Optional, Callable

from execution.live.order_state_machine import (
    OrderStatus, OrderSnapshot, snapshot_from_xt
)


class FillConfirmation:
    def __init__(self, exchange, poll_interval=2.0, timeout=30.0,
                 on_update: Optional[Callable]=None, logger=None):
        self.exchange = exchange
        self.poll_interval = poll_interval
        self.timeout = timeout
        self.on_update = on_update
        self.logger = logger or (lambda msg: None)

    def wait_for_fill(self, order_id: str) -> Optional[OrderSnapshot]:
        start = time.time()
        last_status = None
        last_snapshot = None
        errors = 0

        while True:
            elapsed = time.time() - start
            if elapsed > self.timeout:
                self.logger(f"[Fill] timeout after {elapsed:.1f}s")
                try:
                    snap = self._fetch(order_id)
                    if snap:
                        return snap
                except Exception:
                    pass
                return last_snapshot

            try:
                snap = self._fetch(order_id)
                errors = 0
            except Exception as e:
                errors += 1
                self.logger(f"[Fill] error ({errors}): {e}")
                if errors >= 5:
                    return last_snapshot
                time.sleep(self.poll_interval)
                continue

            if snap is None:
                time.sleep(self.poll_interval)
                continue

            last_snapshot = snap
            if snap.status != last_status:
                self.logger(
                    f"[Fill] {snap.order_id} status={snap.status.value} "
                    f"filled={snap.filled_quantity}/{snap.quantity} "
                    f"avg={snap.avg_fill_price}"
                )
                if self.on_update:
                    try:
                        self.on_update(snap)
                    except Exception as e:
                        self.logger(f"[Fill] on_update error: {e}")
                last_status = snap.status

            if snap.status.is_terminal:
                return snap
            time.sleep(self.poll_interval)

    def _fetch(self, order_id: str) -> Optional[OrderSnapshot]:
        data = self.exchange.get_order(order_id)
        if data:
            return snapshot_from_xt(data)
        try:
            for o in self.exchange.get_open_orders():
                if str(o.get("orderId")) == str(order_id):
                    return snapshot_from_xt(o)
        except Exception:
            pass
        try:
            for o in self.exchange.get_history_orders(order_ids=[order_id]):
                if str(o.get("orderId")) == str(order_id):
                    return snapshot_from_xt(o)
        except Exception:
            pass
        return None