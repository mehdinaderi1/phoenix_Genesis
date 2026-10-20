import json
from pathlib import Path
from datetime import datetime, timezone


class ResilienceManager:
    """State persistence + position recovery."""

    def __init__(self, state_path="data/state.json"):
        self.state_path = Path(state_path)
        self.state_path.parent.mkdir(parents=True, exist_ok=True)

    def save_state(self, cycle_number, session):
        """Atomic write: temp file + rename."""
        state = {
            "version": "1.0",
            "last_cycle": cycle_number,
            "saved_at": datetime.now(timezone.utc).isoformat(),
            "session": session.build_checkpoint(),
        }
        tmp = self.state_path.with_suffix(".tmp")
        tmp.write_text(
            json.dumps(state, indent=2, default=str),
            encoding="utf-8",
        )
        tmp.replace(self.state_path)

    def load_state(self):
        if not self.state_path.exists():
            return None
        try:
            return json.loads(
                self.state_path.read_text(encoding="utf-8")
            )
        except Exception as e:
            print(f"WARNING: state load error: {e}")
            return None

    def clear_state(self):
        if self.state_path.exists():
            self.state_path.unlink()

    def recover_position(self, session, current_price):
        """After reconnect: check if SL/TP was hit during disconnect."""
        position = session.get_position()
        if position is None:
            return None, None
        if not hasattr(position, "should_close_at"):
            return None, None
        should_close, reason, exit_price = position.should_close_at(
            current_price
        )
        if should_close:
            return reason, exit_price
        return None, None