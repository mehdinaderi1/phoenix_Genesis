"""
Live execution adapter — real XT orders (or fake fills in dry-run)
with integrated risk management.
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
from risk.risk_state import RiskState, RiskStateStore
from risk.risk_guard import RiskGuard
from risk.position_sizer import PositionSizer
from risk.kill_switch import KillSwitch

logger = logging.getLogger(__name__)


class _FakeFill:
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
        risk_state_path="data/risk_state.json",
        use_risk_management=True,
        risk_config=None,
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

        # ─── Risk management ───
        self.use_risk_management = use_risk_management
        self.risk_store = RiskStateStore(risk_state_path)
        self.risk_state = self.risk_store.load()
        self.kill_switch = KillSwitch(self.risk_store)

        if use_risk_management:
            cfg = risk_config or {}
            self.risk_guard = RiskGuard(
                max_daily_loss_pct=cfg.get("max_daily_loss_pct", 2.0),
                max_drawdown_pct=cfg.get("max_drawdown_pct", 10.0),
                max_consecutive_losses=cfg.get("max_consecutive_losses", 3),
                max_concurrent_positions=cfg.get("max_concurrent_positions", 1),
            )
            self.position_sizer = PositionSizer(
                risk_per_trade_pct=cfg.get("risk_per_trade_pct", 0.5),
                max_position_pct=cfg.get("max_position_pct", 2.0),
            )
        else:
            self.risk_guard = None
            self.position_sizer = None

        self._log(
            f"[LiveExec] initialized (dry_run={dry_run}, "
            f"risk={'on' if use_risk_management else 'off'})"
        )
        self._log(
            f"[LiveExec] capital={self.risk_state.current_capital:.2f} "
            f"peak={self.risk_state.peak_capital:.2f} "
            f"daily_pnl={self.risk_state.daily_pnl:+.2f}"
        )

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
        ok = self.tracker.load_from_file(self.state_path)
        if not ok:
            self._log(f"[LiveExec] position state load FAILED: {self.state_path}")
            return False
        n = len(self.tracker.positions)
        if n > 0:
            self._log(f"[LiveExec] recovered {n} position(s)")
        return True

    def save_state(self) -> bool:
        ok = self.tracker.save_to_file(self.state_path)
        if not ok:
            self._log(f"[LiveExec] position state save FAILED")
        return ok

    def save_risk_state(self) -> bool:
        ok = self.risk_store.save(self.risk_state)
        if not ok:
            self._log(f"[LiveExec] risk state save FAILED")
        return ok

    def get_position(self, symbol="btc_usdt"):
        return self.tracker.get(symbol)

    def has_position(self, symbol="btc_usdt") -> bool:
        return self.tracker.has_position(symbol)

    # ─── Risk helpers ───
    def _check_risk_gate(self):
        if self.risk_guard is None:
            return {"allowed": True, "reason": "risk_disabled"}
        self.risk_state = self.risk_store.load()
        decision = self.risk_guard.check(
            self.risk_state, len(self.tracker.positions)
        )
        return {"allowed": decision.allowed, "reason": decision.reason}

    def _compute_size(self, side, price, sl):
        if self.position_sizer is None:
            return {"allowed": True, "quantity": None, "notional": None,
                    "reason": "risk_disabled", "sl": sl}
        if sl is None:
            sl = price * (0.99 if side.upper() == "BUY" else 1.01)
            self._log(f"[LiveExec] default SL: {sl:.2f}")
        size = self.position_sizer.compute(
            capital=self.risk_state.current_capital,
            entry_price=price,
            stop_loss=sl,
        )
        return {"allowed": size.allowed, "quantity": size.quantity,
                "notional": size.notional, "reason": size.reason, "sl": sl}

    # ─── OPEN ───
    def open_position(self, symbol, side, price, quantity=None, sl=None, tp=None):
        if self.has_position(symbol):
            self._log(f"[LiveExec] open rejected: position exists for {symbol}")
            return {"action": "HOLD",
                    "execution_result": {"status": "REJECTED"},
                    "reason": "position already open"}

        gate = self._check_risk_gate()
        if not gate["allowed"]:
            self._log(f"[LiveExec] RISK BLOCK: {gate['reason']}")
            return {"action": "BLOCKED",
                    "execution_result": {"status": "BLOCKED"},
                    "reason": gate["reason"]}

        size = self._compute_size(side, price, sl)
        if not size["allowed"]:
            self._log(f"[LiveExec] SIZER BLOCK: {size['reason']}")
            return {"action": "BLOCKED",
                    "execution_result": {"status": "BLOCKED"},
                    "reason": f"sizer: {size['reason']}"}
        if size["quantity"] is not None:
            quantity = size["quantity"]
            self._log(
                f"[LiveExec] sized: qty={quantity} "
                f"notional=${size['notional']} reason={size['reason']}"
            )
        if sl is None:
            sl = size.get("sl")

        if quantity is None or quantity <= 0:
            self._log("[LiveExec] no quantity determined")
            return {"action": "BLOCKED",
                    "execution_result": {"status": "BLOCKED"},
                    "reason": "no_quantity"}

        # DRY-RUN
        if self.dry_run:
            self._log(f"[LiveExec] DRY-RUN would place: {side} {quantity} @ {price}")
            fake = _FakeFill(
                order_id=f"DRY-{int(time.time() * 1000)}",
                filled_qty=quantity, avg_price=price,
            )
            pos = self.tracker.open_from_fill(
                symbol=symbol, side=side, execution_result=fake,
                sl=sl, tp=tp, fee_pct=self.fee_pct,
            )
            self.save_state()
            return {"action": "OPEN",
                    "execution_result": {"status": "DRY_RUN"},
                    "position": pos, "realized_pnl": 0.0,
                    "order_id": fake.order_id, "dry_run": True,
                    "quantity": quantity, "sl": sl, "tp": tp}

        # LIVE
        result = self.executor.execute_limit(
            symbol=symbol, side=side,
            price=f"{price:.2f}", quantity=f"{quantity:.8f}",
        )
        if not result.success:
            self._log(f"[LiveExec] open FAILED: {result}")
            return {"action": "OPEN_FAILED",
                    "execution_result": {"status": result.status.value},
                    "reason": result.error or "not filled"}

        pos = self.tracker.open_from_fill(
            symbol=symbol, side=side, execution_result=result,
            sl=sl, tp=tp, fee_pct=self.fee_pct,
        )
        self.save_state()
        return {"action": "OPEN",
                "execution_result": {"status": "FILLED"},
                "position": pos, "realized_pnl": 0.0,
                "order_id": result.order_id,
                "quantity": quantity, "sl": sl, "tp": tp}

    # ─── CLOSE ───
    def close_position(self, symbol, current_price, reason="manual"):
        pos = self.tracker.get(symbol)
        if pos is None:
            return {"action": "HOLD",
                    "execution_result": {"status": "REJECTED"},
                    "reason": "no position"}

        # DRY-RUN close
        if self.dry_run:
            self._log(f"[LiveExec] DRY-RUN would close {pos.side} {pos.quantity} @ MARKET")
            fake = _FakeFill(
                order_id=f"DRY-CLOSE-{int(time.time() * 1000)}",
                filled_qty=pos.quantity, avg_price=current_price,
            )
            closed = self.tracker.close_from_fill(
                symbol=symbol, execution_result=fake, fee_pct=self.fee_pct,
            )
            self.save_state()
            if self.use_risk_management:
                self.risk_state.record_trade(closed["realized_pnl"])
                self.save_risk_state()
                self._log(
                    f"[LiveExec] risk recorded: pnl={closed['realized_pnl']:+.6f} "
                    f"daily={self.risk_state.daily_pnl:+.2f} "
                    f"consec_losses={self.risk_state.consecutive_losses}"
                )
            return {"action": "CLOSE",
                    "execution_result": {"status": "DRY_RUN"},
                    "position": None,
                    "realized_pnl": closed["realized_pnl"],
                    "order_id": fake.order_id,
                    "close_reason": reason, "dry_run": True}

        # LIVE close
        close_side = "SELL" if pos.side == "BUY" else "BUY"
        agg_price = current_price * (0.995 if pos.side == "BUY" else 1.005)
        result = self.executor.execute_limit(
            symbol=symbol, side=close_side,
            price=f"{agg_price:.2f}",
            quantity=f"{pos.quantity:.8f}",
            timeout=15.0,
        )
        if not result.success:
            self._log(f"[LiveExec] close FAILED: {result}")
            return {"action": "CLOSE_FAILED",
                    "execution_result": {"status": result.status.value},
                    "reason": result.error or "not filled"}

        closed = self.tracker.close_from_fill(
            symbol=symbol, execution_result=result, fee_pct=self.fee_pct,
        )
        self.save_state()
        if self.use_risk_management:
            self.risk_state.record_trade(closed["realized_pnl"])
            self.save_risk_state()
            self._log(
                f"[LiveExec] risk recorded: pnl={closed['realized_pnl']:+.6f} "
                f"daily={self.risk_state.daily_pnl:+.2f} "
                f"consec_losses={self.risk_state.consecutive_losses}"
            )
        return {"action": "CLOSE",
                "execution_result": {"status": "FILLED"},
                "position": None,
                "realized_pnl": closed["realized_pnl"],
                "order_id": result.order_id,
                "close_reason": reason}