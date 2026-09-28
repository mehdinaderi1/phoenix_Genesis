from execution.execution_result import ExecutionResult
from execution.paper_position_manager import PaperPositionManager


class XTFuturesPositionBridge:
    """
    Bridges a confirmed XT ExecutionResult into the
    existing Phoenix Position Manager.

    This class does not create PaperPosition directly.
    Position creation remains owned by PaperPositionManager.
    """

    def __init__(self, position_manager=None):
        self.position_manager = (
            position_manager or PaperPositionManager()
        )

    def apply(self, execution_result, decision=None):
        if not isinstance(
            execution_result,
            ExecutionResult,
        ):
            raise TypeError(
                "execution_result must be ExecutionResult"
            )

        if execution_result.status != "EXECUTED":
            return None

        return self.position_manager.open_position(
            execution_result,
            decision=decision,
        )

    def get_position(self):
        return self.position_manager.get_position()
