import os

from config.settings import Settings
from execution.paper_position import _cfg_bool, _cfg_float


class PaperPositionLifecycle:

    def __init__(self, session):
        self.session = session

    def process(self, action_proposal, price, symbol="BTCUSDT", decision=None):
        position = self.session.get_position()
        action = getattr(action_proposal, "action", None)

        # آپدیت best price برای trailing
        if position is not None:
            position.update_best_price(price)

        # ۱. SL/TP/Timeout (بالاترین اولویت)
        _auto_sl_tp = (
            os.getenv("PHOENIX_AUTO_SL_TP", "0").strip() == "1"
            or getattr(Settings, "AUTO_TP_SL", False)
        )
        if position is not None and _auto_sl_tp:
            should_close, reason, exit_price = position.should_close_at(price)
            if should_close:
                closed = self.session.close_position(exit_price=exit_price)
                if closed is not None:
                    return self._close_result(closed, reason)

        # ۲. Partial close
        partial_data = None
        if position is not None:
            frac = position.should_partial_close(price)
            if frac:
                partial_data = self.session.position_manager.partial_close(
                    price, frac
                )
                if partial_data:
                    self.session.portfolio.apply_realized_pnl(
                        partial_data["partial_pnl"]
                    )
                    print(
                        f"PARTIAL: closed "
                        f"{partial_data['closed_quantity']:.6f} @ "
                        f"{price:.2f}, "
                        f"PnL={partial_data['partial_pnl']:+.4f}, "
                        f"remaining="
                        f"{partial_data['remaining_quantity']:.6f}"
                    )

                    # ─── TP را گسترش بده تا trailing فضای مانور داشته باشد ───
                    if _cfg_bool("PARTIAL_TP_ENABLED", False):
                        extend_R = _cfg_float(
                            "TP_EXTEND_AFTER_PARTIAL_R", 3.0
                        )
                        risk = position._risk_distance()
                        if risk > 0:
                            if position.side == "BUY":
                                new_tp = position.entry_price + risk * extend_R
                            else:
                                new_tp = position.entry_price - risk * extend_R
                            old_tp = position.tp
                            position.tp = new_tp
                            print(
                                f"TP_EXTEND: {old_tp:.2f} → {new_tp:.2f} "
                                f"(from 2R to {extend_R:.1f}R)"
                            )

        

        # ۳. SL move (BE / trailing)
        sl_data = None
        if position is not None:
            new_sl = position.should_move_sl(price)
            if new_sl is not None:
                old_sl = position.sl
                self.session.position_manager.move_sl(new_sl)
                sl_data = {"old_sl": old_sl, "new_sl": new_sl}
                print(f"SL_MOVE: {old_sl:.2f} → {new_sl:.2f}")

        # ۴. اگر پوزیشن None بود → OPEN
        if position is None:
            if action in ("BUY", "SELL"):
                result = self.session.process_action(
                    action_proposal=action_proposal,
                    price=price,
                    symbol=symbol,
                    decision=decision,
                )
                if result["position"] is not None:
                    return {
                        "action": "OPEN",
                        "execution_result": result["execution_result"],
                        "position": result["position"],
                        "realized_pnl": 0.0,
                        "partial_info": None,
                        "sl_move_info": None,
                    }
            return self._hold_result(None, partial_data, sl_data)

        # ۵. اگر Partial یا SL move فعال شد → گزارش
        if partial_data is not None:
            return {
                "action": "PARTIAL",
                "position": position,
                "realized_pnl": partial_data["partial_pnl"],
                "partial_info": partial_data,
                "sl_move_info": sl_data,
            }

        if sl_data is not None:
            return {
                "action": "SL_MOVE",
                "position": position,
                "realized_pnl": 0.0,
                "partial_info": None,
                "sl_move_info": sl_data,
            }

        # ۶. منطق اصلی
        if action == "WAIT":
            return self._hold_result(position, None, None)

        if action in ("BUY", "SELL") and action != position.side:
            closed = self.session.close_position(exit_price=price)
            if closed is None:
                return self._hold_result(position, None, None)
            return self._close_result(closed, "OPPOSITE_SIGNAL")

        return self._hold_result(position, None, None)

    def _hold_result(self, position, partial_data, sl_data):
        return {
            "action": "HOLD",
            "position": position,
            "realized_pnl": 0.0,
            "partial_info": partial_data,
            "sl_move_info": sl_data,
        }

    def _close_result(self, closed, reason):
        return {
            "action": "CLOSE",
            "position": closed["position"],
            "exit_price": closed["exit_price"],
            "realized_pnl": closed["realized_pnl"],
            "trade": closed["trade"],
            "learning_result": closed.get("learning_result"),
            "close_reason": reason,
            "partial_info": None,
            "sl_move_info": None,
        }