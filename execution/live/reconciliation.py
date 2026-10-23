"""
Reconciliation — compare Phoenix's tracked positions with XT balances.
Prevents acting on stale / orphaned state after restart.
"""
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class ReconciliationResult:
    def __init__(self):
        self.missing_on_xt: List[str] = []
        self.orphan_on_xt: List[str] = []
        self.quantity_mismatch: List[dict] = []
        self.clean: bool = True

    def __repr__(self):
        return (
            f"<Reconcile clean={self.clean} "
            f"missing={len(self.missing_on_xt)} "
            f"orphan={len(self.orphan_on_xt)} "
            f"qty_mismatch={len(self.quantity_mismatch)}>"
        )


class LiveReconciler:
    def __init__(self, exchange, tolerance_pct: float = 0.001):
        self.exchange = exchange
        self.tolerance_pct = tolerance_pct

    def reconcile(self, tracker) -> ReconciliationResult:
        result = ReconciliationResult()

        try:
            balances = self.exchange.fetch_balances()
        except Exception as e:
            logger.error(f"reconcile: fetch_balances failed: {e}")
            result.clean = False
            return result

        xt_balances = {}
        for b in balances:
            cur = (b.get("currency") or "").lower()
            avail = float(b.get("availableAmount") or 0)
            total = float(b.get("totalAmount") or 0)
            if total > 0:
                xt_balances[cur] = {"available": avail, "total": total}

        for symbol, pos in tracker.positions.items():
            base = symbol.split("_")[0].lower() if "_" in symbol else symbol[:3].lower()

            if pos.side == "BUY":
                xt_qty = xt_balances.get(base, {}).get("total", 0)
                diff = abs(xt_qty - pos.quantity) / max(pos.quantity, 1e-10)
                if xt_qty == 0 and pos.quantity > 0:
                    result.missing_on_xt.append(symbol)
                    result.clean = False
                    logger.warning(f"reconcile: {symbol} tracked qty={pos.quantity} "
                                   f"but XT balance=0")
                elif diff > self.tolerance_pct:
                    result.quantity_mismatch.append({
                        "symbol": symbol, "tracked": pos.quantity,
                        "on_xt": xt_qty, "diff_pct": diff * 100,
                    })
                    result.clean = False
                    logger.warning(f"reconcile: {symbol} tracked={pos.quantity} "
                                   f"xt={xt_qty} diff={diff*100:.2f}%")

        return result


def reconcile_or_refuse(tracker, exchange) -> bool:
    """Convenience: return True only if clean."""
    r = LiveReconciler(exchange).reconcile(tracker)
    if not r.clean:
        logger.error(f"RECONCILIATION FAILED: {r}")
        return False
    logger.info(f"Reconciliation OK: {r}")
    return True