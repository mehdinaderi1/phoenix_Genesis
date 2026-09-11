class PaperSessionPerformance:

    def analyze(self, session):
        summary = session.get(
            "summary",
            {}
        )

        cycles = session.get(
            "cycles",
            []
        )

        trade_count = summary.get(
            "trade_count",
            0
        )

        total_pnl = summary.get(
            "total_pnl",
            0.0
        )

        winning_trades = [
            cycle
            for cycle in cycles
            if cycle.get(
                "realized_pnl"
            ) is not None
            and cycle.get(
                "realized_pnl"
            ) > 0
        ]

        losing_trades = [
            cycle
            for cycle in cycles
            if cycle.get(
                "realized_pnl"
            ) is not None
            and cycle.get(
                "realized_pnl"
            ) < 0
        ]

        win_count = len(
            winning_trades
        )

        loss_count = len(
            losing_trades
        )

        win_rate = (
            win_count / trade_count * 100
            if trade_count > 0
            else 0.0
        )

        average_pnl = (
            total_pnl / trade_count
            if trade_count > 0
            else 0.0
        )

        return {
            "cycles_processed": summary.get(
                "cycles_processed",
                len(cycles)
            ),
            "trade_count": trade_count,
            "win_count": win_count,
            "loss_count": loss_count,
            "win_rate": win_rate,
            "total_pnl": total_pnl,
            "average_pnl": average_pnl
        }
