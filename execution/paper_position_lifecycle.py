import os
from config.settings import Settings

class PaperPositionLifecycle:

    def __init__(self, session):
        self.session = session

    def process(
        self,
        action_proposal,
        price,
        symbol="BTCUSDT",
        decision=None,
    ):
        position = self.session.get_position()
        action = getattr(action_proposal, "action", None)

        # ─── SL/TP/Timeout check (before any other logic) ───
        _auto_sl_tp = (
            os.getenv("PHOENIX_AUTO_SL_TP", "0").strip() == "1"
            or getattr(Settings, "AUTO_TP_SL", False)
        )
        if position is not None and _auto_sl_tp:
            should_close, reason, exit_price = position.should_close_at(price)
            if should_close:
                closed = self.session.close_position(exit_price=exit_price)
                if closed is not None:
                    return {
                        "action": "CLOSE",
                        "position": closed["position"],
                        "exit_price": closed["exit_price"],
                        "realized_pnl": closed["realized_pnl"],
                        "trade": closed["trade"],
                        "learning_result": closed.get("learning_result"),
                        "close_reason": reason,
                    }

        # ─── Original logic (unchanged) ───
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
                    }
            return {"action": "HOLD", "position": None, "realized_pnl": 0.0}

        if action == "WAIT":
            return {"action": "HOLD", "position": position, "realized_pnl": 0.0}

        if action in ("BUY", "SELL") and action != position.side:
            closed = self.session.close_position(exit_price=price)
            if closed is None:
                return {"action": "HOLD", "position": position, "realized_pnl": 0.0}
            return {
                "action": "CLOSE",
                "position": closed["position"],
                "exit_price": closed["exit_price"],
                "realized_pnl": closed["realized_pnl"],
                "trade": closed["trade"],
                "learning_result": closed.get("learning_result"),
                "close_reason": "OPPOSITE_SIGNAL",
            }

        return {"action": "HOLD", "position": position, "realized_pnl": 0.0}