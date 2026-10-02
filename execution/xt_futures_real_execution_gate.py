class XTFuturesRealExecutionGate:
    """Explicit safety gate for real XT Futures execution."""

    def __init__(
        self,
        demo_mode,
        real_execution_enabled=False,
    ):
        self.demo_mode = demo_mode
        self.real_execution_enabled = real_execution_enabled

    @property
    def is_authorized(self):
        return (
            self.demo_mode is False
            and self.real_execution_enabled is True
        )

    def authorize(self):
        if not self.is_authorized:
            raise PermissionError(
                "Real execution is blocked by the safety gate."
            )

        return True
