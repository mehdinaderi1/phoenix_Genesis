"""
Risk guard — gatekeeper that decides allow / block for each trade.
"""
import logging
from dataclasses import dataclass
from typing import Optional

from risk.risk_state import RiskState

logger = logging.getLogger(__name__)


@dataclass
class RiskDecision:
    allowed: bool
    reason: str
    size_cap_pct: Optional[float] = None


class RiskGuard:
    def __init__(
        self,
        max_daily_loss_pct: float = 2.0,
        max_drawdown_pct: float = 10.0,
        max_consecutive_losses: int = 3,
        max_concurrent_positions: int = 1,
    ):
        self.max_daily_loss_pct = max_daily_loss_pct
        self.max_drawdown_pct = max_drawdown_pct
        self.max_consecutive_losses = max_consecutive_losses
        self.max_concurrent_positions = max_concurrent_positions

    def check(
        self,
        state: RiskState,
        current_position_count: int = 0,
    ) -> RiskDecision:
        # 1. Kill switch
        if state.kill_switch_active:
            return RiskDecision(
                False,
                f"kill_switch: {state.kill_switch_reason}",
            )

        # 2. Daily loss limit
        daily_loss = state.daily_loss_pct()
        if daily_loss >= self.max_daily_loss_pct:
            return RiskDecision(
                False,
                f"daily_loss_{daily_loss:.2f}%_>=_{self.max_daily_loss_pct}%",
            )

        # 3. Total drawdown
        dd = state.drawdown_pct()
        if dd >= self.max_drawdown_pct:
            return RiskDecision(
                False,
                f"drawdown_{dd:.2f}%_>=_{self.max_drawdown_pct}%",
            )

        # 4. Consecutive losses
        if state.consecutive_losses >= self.max_consecutive_losses:
            return RiskDecision(
                False,
                f"consecutive_losses_{state.consecutive_losses}",
            )

        # 5. Concurrent positions
        if current_position_count >= self.max_concurrent_positions:
            return RiskDecision(
                False,
                f"max_positions_{self.max_concurrent_positions}",
            )

        return RiskDecision(True, "ok")