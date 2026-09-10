from execution.paper_trade_record import PaperTradeRecord


class PaperTradeHistory:

    def __init__(self):
        self.trades = []

    def add_trade(
        self,
        position,
        exit_price,
        realized_pnl
    ):

        record = PaperTradeRecord(
            symbol=position.symbol,
            side=position.side,
            entry_price=position.entry_price,
            exit_price=exit_price,
            quantity=position.quantity,
            realized_pnl=realized_pnl
        )

        self.trades.append(record)

        return record

    def get_trades(self):

        return list(self.trades)

    def get_trade_count(self):

        return len(self.trades)

    def get_total_realized_pnl(self):

        return sum(
            trade.realized_pnl
            for trade in self.trades
        )