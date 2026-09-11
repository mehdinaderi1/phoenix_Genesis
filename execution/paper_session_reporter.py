class PaperSessionReporter:

    def build_report(
        self,
        session_id,
        session,
        performance
    ):
        return {
            "session_id": session_id,
            "cycles": performance.get(
                "cycles_processed",
                len(session.get("cycles", []))
            ),
            "trade_count": performance.get(
                "trade_count",
                0
            ),
            "win_count": performance.get(
                "win_count",
                0
            ),
            "loss_count": performance.get(
                "loss_count",
                0
            ),
            "win_rate": performance.get(
                "win_rate",
                0.0
            ),
            "total_pnl": performance.get(
                "total_pnl",
                0.0
            ),
            "average_pnl": performance.get(
                "average_pnl",
                0.0
            ),
            "final_position": session.get(
                "final_position"
            )
        }
