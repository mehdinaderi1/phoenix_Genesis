"""
Kill switch — emergency stop. Can be triggered manually or automatically.

Usage:
    ks = KillSwitch(store)
    ks.trigger("manual", "operator request")
    ks.is_active()  # True
    ks.release()
"""
import logging
from datetime import datetime, timezone
from typing import Optional

from risk.risk_state import RiskState, RiskStateStore

logger = logging.getLogger(__name__)


class KillSwitch:
    def __init__(self, store: RiskStateStore):
        self.store = store

    def is_active(self) -> bool:
        return self.store.load().kill_switch_active

    def trigger(self, reason: str, message: str = "") -> None:
        state = self.store.load()
        full_reason = f"{reason}: {message}" if message else reason
        state.activate_kill_switch(full_reason)
        self.store.save(state)
        logger.critical(f"KillSwitch triggered: {full_reason}")

    def release(self) -> None:
        state = self.store.load()
        state.deactivate_kill_switch()
        # Reset consecutive losses on manual release
        state.consecutive_losses = 0
        self.store.save(state)
        logger.info("KillSwitch released")