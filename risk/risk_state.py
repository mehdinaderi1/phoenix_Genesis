"""
Risk state — persistent tracking of capital, drawdown, daily PnL.
"""
import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, date
from pathlib import Path
from typing import Optional, List

logger = logging.getLogger(__name__)


@dataclass
class RiskState:
    initial_capital: float = 1000.0
    current_capital: float = 1000.0
    peak_capital: float = 1000.0

    # Daily tracking (reset at midnight UTC)
    today_date: str = ""              # "2026-10-23"
    daily_pnl: float = 0.0
    daily_trades: int = 0

    # Consecutive tracking
    consecutive_losses: int = 0
    consecutive_wins: int = 0

    # Lifetime
    total_trades: int = 0
    total_wins: int = 0
    total_losses: int = 0

    # Kill switch
    kill_switch_active: bool = False
    kill_switch_reason: str = ""
    kill_switch_since: str = ""

    # Recent PnL history (for drawdown)
    recent_pnl: List[float] = field(default_factory=list)

    def _today(self) -> str:
        return datetime.now(timezone.utc).date().isoformat()

    def _reset_daily_if_needed(self) -> None:
        today = self._today()
        if self.today_date != today:
            self.today_date = today
            self.daily_pnl = 0.0
            self.daily_trades = 0

    def record_trade(self, pnl: float) -> None:
        """Record a closed trade result."""
        self._reset_daily_if_needed()

        self.current_capital += pnl
        self.daily_pnl += pnl
        self.daily_trades += 1
        self.total_trades += 1

        if pnl > 0:
            self.consecutive_wins += 1
            self.consecutive_losses = 0
            self.total_wins += 1
        elif pnl < 0:
            self.consecutive_losses += 1
            self.consecutive_wins = 0
            self.total_losses += 1

        if self.current_capital > self.peak_capital:
            self.peak_capital = self.current_capital

        self.recent_pnl.append(pnl)
        if len(self.recent_pnl) > 100:
            self.recent_pnl = self.recent_pnl[-100:]

    def drawdown_pct(self) -> float:
        if self.peak_capital <= 0:
            return 0.0
        return (self.peak_capital - self.current_capital) / self.peak_capital * 100

    def daily_loss_pct(self) -> float:
        if self.initial_capital <= 0:
            return 0.0
        if self.daily_pnl >= 0:
            return 0.0
        return abs(self.daily_pnl) / self.initial_capital * 100

    def activate_kill_switch(self, reason: str) -> None:
        if self.kill_switch_active:
            return
        self.kill_switch_active = True
        self.kill_switch_reason = reason
        self.kill_switch_since = datetime.now(timezone.utc).isoformat()
        logger.critical(f"KILL SWITCH ACTIVATED: {reason}")

    def deactivate_kill_switch(self) -> None:
        self.kill_switch_active = False
        self.kill_switch_reason = ""
        self.kill_switch_since = ""
        logger.info("KILL SWITCH deactivated")


class RiskStateStore:
    """Persistence for RiskState."""

    VERSION = 1

    def __init__(self, path="data/risk_state.json"):
        self.path = Path(path)

    def save(self, state: RiskState) -> bool:
        try:
            payload = {
                "version": self.VERSION,
                "saved_at": datetime.now(timezone.utc).isoformat(),
                "state": asdict(state),
            }
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_suffix(".tmp")
            tmp.write_text(
                json.dumps(payload, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            tmp.replace(self.path)
            return True
        except Exception as e:
            logger.error(f"RiskState save failed: {e}")
            return False

    def load(self) -> RiskState:
        if not self.path.exists():
            return RiskState()

        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except Exception as e:
            logger.error(f"RiskState corrupted: {e}")
            return RiskState()

        if raw.get("version") != self.VERSION:
            logger.warning(f"RiskState version mismatch")
            return RiskState()

        data = raw.get("state", {})
        state = RiskState()
        for k, v in data.items():
            if hasattr(state, k):
                setattr(state, k, v)
        state._reset_daily_if_needed()
        return state