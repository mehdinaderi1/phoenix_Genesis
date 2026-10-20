import os

from notifications.telegram_sender import TelegramSender


class PositionNotifier:
    """Send position open/close notifications to Telegram."""

    def __init__(self):
        self.enabled = (
            os.getenv("PHOENIX_TELEGRAM_ENABLED", "0").strip() == "1"
        )
        self.sender = None
        if self.enabled:
            try:
                self.sender = TelegramSender()
            except ValueError as e:
                print(f"WARNING: Telegram notifier disabled: {e}")
                self.enabled = False

    def _send(self, text):
        if not self.enabled or self.sender is None:
            return
        try:
            self.sender.send_message(text)
        except Exception as e:
            print(f"WARNING: Telegram send failed: {e}")

    def notify_open(self, position):
        if position is None:
            return
        try:
            sl = getattr(position, "sl", None)
            tp = getattr(position, "tp", None)
            lev = float(getattr(position, "leverage", 1.0))
            qty = float(getattr(position, "quantity", 0))
            entry = float(getattr(position, "entry_price", 0))
            notional = qty * entry
            margin = notional / max(lev, 1.0)

            text = (
                f"[OPEN] Position opened\n"
                f"Symbol: {position.symbol}\n"
                f"Side: {position.side}\n"
                f"Leverage: {lev:g}x\n"
                f"Entry: {entry:.2f}\n"
                f"Qty: {qty:.6f}\n"
                f"Notional: {notional:.2f} USDT\n"
                f"Margin: {margin:.2f} USDT\n"
            )
            text += f"SL: {sl:.2f}" if sl else "SL: N/A"
            text += f"\nTP: {tp:.2f}" if tp else "\nTP: N/A"
            self._send(text)
        except Exception as e:
            print(f"WARNING: notify_open failed: {e}")

    def notify_close(self, position, exit_price, pnl, reason="UNKNOWN"):
        if position is None:
            return
        try:
            tag = "OK" if pnl >= 0 else "LOSS"
            lev = float(getattr(position, "leverage", 1.0))
            qty = float(getattr(position, "quantity", 0))
            entry = float(getattr(position, "entry_price", 0))
            notional = qty * entry
            margin = notional / max(lev, 1.0)
            pnl_pct_on_margin = (pnl / margin * 100) if margin > 0 else 0.0

            text = (
                f"[CLOSE] [{tag}] Position closed\n"
                f"Symbol: {position.symbol}\n"
                f"Side: {position.side}\n"
                f"Leverage: {lev:g}x\n"
                f"Entry: {entry:.2f}\n"
                f"Exit: {exit_price:.2f}\n"
                f"Qty: {qty:.6f}\n"
                f"Notional: {notional:.2f} USDT\n"
                f"Margin: {margin:.2f} USDT\n"
                f"PnL: {pnl:+.4f} USDT ({pnl_pct_on_margin:+.2f}% on margin)\n"
                f"Reason: {reason}"
            )
            self._send(text)
        except Exception as e:
            print(f"WARNING: notify_close failed: {e}")

    def notify_partial(self, position, closed_qty, partial_pnl, exit_price):
        if position is None:
            return
        try:
            sl = getattr(position, "sl", None)
            tp = getattr(position, "tp", None)
            remaining = float(getattr(position, "quantity", 0))
            text = (
                f"[PARTIAL] Partial close\n"
                f"Symbol: {position.symbol}\n"
                f"Side: {position.side}\n"
                f"Exit: {exit_price:.2f}\n"
                f"Closed Qty: {closed_qty:.6f}\n"
                f"Remaining Qty: {remaining:.6f}\n"
                f"Partial PnL: {partial_pnl:+.4f} USDT\n"
            )
            text += f"New SL: {sl:.2f}\n" if sl else "SL: N/A\n"
            text += f"New TP: {tp:.2f}" if tp else "TP: N/A"
            self._send(text)
        except Exception as e:
            print(f"WARNING: notify_partial failed: {e}")

    def notify_sl_move(self, position, old_sl, new_sl):
        if position is None:
            return
        try:
            text = (
                f"[SL_MOVE] Stop-loss moved\n"
                f"Symbol: {position.symbol}\n"
                f"Side: {position.side}\n"
                f"Old SL: {old_sl:.2f}\n"
                f"New SL: {new_sl:.2f}"
            )
            self._send(text)
        except Exception as e:
            print(f"WARNING: notify_sl_move failed: {e}")