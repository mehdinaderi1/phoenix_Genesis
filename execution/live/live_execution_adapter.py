"""
Live execution adapter — mirrors paper_trading_runtime interface
but places real orders on XT (or fake fills in dry-run).
"""
import os
import time
import logging
from typing import Optional

from exchanges.xt_private_exchange import XTPrivateExchange
from execution.live.order_executor import OrderExecutor
from execution.live.position_tracker import LivePositionTracker
from execution.live.reconciliation import LiveReconciler
from execution.live.order_state_machine import OrderStatus

logger = logging.getLogger(__name__)


class _FakeFill:
    """Simulated fill for dry-run mode."""
    def __init__(self, order_id, filled_qty, avg_price):
        self.success = True
        self.order_id = order_id
        self.status = OrderStatus.FILLED
        self.filled_quantity = float(filled_qty)
        self.avg_fill_price = float(avg_price)
        self.total_cost = self.filled_quantity * self.avg_fill_price
        self.raw_snapshot = None
        self.error = None


class LiveExecutionAdapter:
    def __init__(
        self,
        api_key=None,
        api_secret=None,
        fee_pct=0.0006,
        default_timeout=30.0,
        poll_interval=2.0,
        dry_run=False,
        state_path="data/live_positions.json",
    ):
        self.exchange = XTPrivateExchange(
            api_key=api_key or os.getenv("XT_API_KEY"),
            api_secret=api_secret or os.getenv("XT_API_SECRET"),
        )
        self.state_path = state_path
        self.executor = OrderExecutor(
            self.exchange,
            default_timeout=default_timeout,
            poll_interval=poll_interval,
            logger=self._log,
        )
        self.tracker = LivePositionTracker()
        self.reconciler = LiveReconciler(self.exchange)
        self.fee_pct = fee_pct
        self.dry_run = dry_run
        self._log(f"[LiveExec] initialized (dry_run={dry_run})")

    def _log(self, msg):
        logger.info(msg)
        print(msg)

    def reconcile_or_refuse(self) -> bool:
        r = self.reconciler.reconcile(self.tracker)
        if not r.clean:
            self._log(f"[LiveExec] RECONCILE FAILED: {r}")
            return False
        self._log(f"[LiveExec] reconciled OK")
        return True

    def load_state(self) -> bool:
        """Load prior positions. Returns False on hard failure."""
        ok = self.tracker.load_from_file(self.state_path)
        if not ok:
            self._log(f"[LiveExec] state load FAILED: {self.state_path}")
            return False
        count = len(self.tracker.positions)
        if count > 0:
            self._log(f"[LiveExec] recovered {count} position(s) from disk")
        return True

    def save_state(self) -> bool:
        """Persist current positions. Returns True on success."""
        ok = self.tracker.save_to_file(self.state_path)
        if not ok:
            self._log(f"[LiveExec] state save FAILED: {self.state_path}")
        return ok

    def get_position(self, symbol="btc_usdt"):
        return self.tracker.get(symbol)

    def has_position(self, symbol="btc_usdt") -> bool:
        return self.tracker.has_position(symbol)

    # ─────────────────────────────────────────────
    # OPEN
    # ─────────────────────────────────────────────
    def open_position(
        self, symbol, side, price, quantity, sl=None, tp=None
    ) -> dict:
        if self.has_position(symbol):
            self._log(f"[LiveExec] open rejected: position already exists for {symbol}")
            return {
                "action": "HOLD",
                "execution_result": {"status": "REJECTED"},
                "reason": "position already open",
            }

        # ─── DRY-RUN: simulate fill ───
        if self.dry_run:
            self._log(f"[LiveExec] DRY-RUN would place: {side} {quantity} @ {price}")

            fake = _FakeFill(
                order_id=f"DRY-{int(time.time() * 1000)}",
                filled_qty=quantity,
                avg_price=price,
            )
            pos = self.tracker.open_from_fill(
                symbol=symbol, side=side, execution_result=fake,
                sl=sl, tp=tp, fee_pct=self.fee_pct,
            )
            self.save_state()
            return {
                "action": "OPEN",
                "execution_result": {"status": "DRY_RUN"},
                "position": pos,
                "realized_pnl": 0.0,
                "order_id": fake.order_id,
                "dry_run": True,
            }

        # ─── LIVE: real order ───
        result = self.executor.execute_limit(
            symbol=symbol, side=side,
            price=f"{price:.2f}", quantity=f"{quantity:.8f}",
        )

        if not result.success:
            self._log(f"[LiveExec] open FAILED: {result}")
            return {
                "action": "OPEN_FAILED",
                "execution_result": {"status": result.status.value},
                "reason": result.error or "not filled",
            }

        pos = self.tracker.open_from_fill(
            symbol=symbol, side=side, execution_result=result,
            sl=sl, tp=tp, fee_pct=self.fee_pct,
        )
        return {
            "action": "OPEN",
            "execution_result": {"status": "FILLED"},
            "position": pos,
            "realized_pnl": 0.0,
            "order_id": result.order_id,
        }

    # ─────────────────────────────────────────────
    # CLOSE
    # ─────────────────────────────────────────────
    def close_position(
        self, symbol, current_price, reason="manual"
    ) -> dict:
        pos = self.tracker.get(symbol)
        if pos is None:
            return {
                "action": "HOLD",
                "execution_result": {"status": "REJECTED"},
                "reason": "no position",
            }

        # ─── DRY-RUN: simulate close ───
        if self.dry_run:
            self._log(
                f"[LiveExec] DRY-RUN would close "
                f"{pos.side} {pos.quantity} @ MARKET"
            )

            fake = _FakeFill(
                order_id=f"DRY-CLOSE-{int(time.time() * 1000)}",
                filled_qty=pos.quantity,
                avg_price=current_price,
            )
            closed = self.tracker.close_from_fill(
                symbol=symbol, execution_result=fake, fee_pct=self.fee_pct,
            )

            self.save_state()
            return {
                "action": "CLOSE",
                "execution_result": {"status": "DRY_RUN"},
                "position": None,
                "realized_pnl": closed["realized_pnl"],
                "order_id": fake.order_id,
                "close_reason": reason,
                "dry_run": True,
            }

        # ─── LIVE: real close ───
        close_side = "SELL" if pos.side == "BUY" else "BUY"
        if pos.side == "BUY":
            aggressive_price = current_price * 0.995
        else:
            aggressive_price = current_price * 1.005

        result = self.executor.execute_limit(
            symbol=symbol, side=close_side,
            price=f"{aggressive_price:.2f}",
            quantity=f"{pos.quantity:.8f}",
            timeout=15.0,
        )

        if not result.success:
            self._log(f"[LiveExec] close FAILED: {result}")
            return {
                "action": "CLOSE_FAILED",
                "execution_result": {"status": result.status.value},
                "reason": result.error or "not filled",
            }

        closed = self.tracker.close_from_fill(
            symbol=symbol, execution_result=result, fee_pct=self.fee_pct,
        )
        self.save_state()
        return {
            "action": "CLOSE",
            "execution_result": {"status": "FILLED"},
            "position": None,
            "realized_pnl": closed["realized_pnl"],
            "order_id": result.order_id,
            "close_reason": reason,
        }