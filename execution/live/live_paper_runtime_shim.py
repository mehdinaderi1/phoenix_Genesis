"""
LivePaperRuntimeShim — mimics PaperTradingRuntime.run() interface
but routes to LiveExecutionAdapter (which places real orders).

This is the bridge between operational_runtime and live execution.
"""
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)


class LivePaperRuntimeShim:
    def __init__(self, live_adapter):
        self.live = live_adapter
        self.session = None            # operational_runtime may access .session
        self.trade_history = None      # may access .trade_history

    def run(self, cycles: List[dict], symbol: str) -> List[dict]:
        """
        cycles is typically [paper_input] where paper_input has:
        - action_proposal (translated)
        - price
        - symbol
        - decision

        Returns [paper_result_compatible_dict].
        """
        if not cycles:
            return [self._hold(symbol, "empty_cycles")]

        inp = cycles[0]
        action = (getattr(inp.get("action_proposal"), "action", None) or "HOLD").upper()
        price = inp.get("price")

        # Normalize symbol: BTCUSDT -> btc_usdt
        if "_" not in symbol:
            base = symbol.replace("USDT", "").replace("USDC", "").replace("BTC", "")
            quote = "usdt" if "USDT" in symbol else "usdc" if "USDC" in symbol else "usdt"
            base = symbol.replace(quote.upper(), "").lower()
            xt_symbol = f"{base}_{quote}"
        else:
            xt_symbol = symbol.lower()

        if action in ("BUY", "SELL"):
            return [self._handle_open(xt_symbol, action, price, inp)]

        if action in ("CLOSE", "SELL_CLOSE"):
            return [self._handle_close(xt_symbol, price)]

        # HOLD, WAIT, etc.
        return [self._hold(symbol, f"action={action}")]

    def _handle_open(self, symbol, side, price, inp) -> dict:
        if self.live.has_position(symbol):
            return self._hold(symbol, "position_open")

        # Compute quantity from decision metadata or use default
        qty = self._estimate_quantity(price)
        if qty <= 0:
            return self._hold(symbol, "qty_zero")

        try:
            result = self.live.open_position(
                symbol=symbol, side=side, price=price, quantity=qty,
                sl=None, tp=None,
            )
        except Exception as e:
            logger.exception(f"LivePaperRuntimeShim open failed: {e}")
            return {
                "action": "OPEN_FAILED",
                "execution_result": {"status": "ERROR"},
                "error": str(e),
            }

        return result

    def _handle_close(self, symbol, price) -> dict:
        if not self.live.has_position(symbol):
            return self._hold(symbol, "no_position_to_close")
        try:
            return self.live.close_position(symbol, current_price=price, reason="signal")
        except Exception as e:
            logger.exception(f"LivePaperRuntimeShim close failed: {e}")
            return {
                "action": "CLOSE_FAILED",
                "execution_result": {"status": "ERROR"},
                "error": str(e),
            }

    def _estimate_quantity(self, price, margin_usd=10.0) -> float:
        if not price or price <= 0:
            return 0.0
        qty = margin_usd / price
        # Round to 5 decimals for BTC (exchange precision)
        return round(qty, 5)

    def _hold(self, symbol, reason) -> dict:
        return {
            "action": "HOLD",
            "execution_result": {"status": "SKIPPED"},
            "reason": reason,
            "realized_pnl": 0.0,
        }

    def get_position(self, symbol="btc_usdt"):
        return self.live.get_position(symbol)

    def get_balance(self):
        try:
            balances = self.live.exchange.fetch_balances()
            for b in balances:
                if b.get("currency", "").lower() == "usdt":
                    return float(b.get("totalAmount", 0))
        except Exception:
            pass
        return 0.0