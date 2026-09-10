from dataclasses import dataclass


@dataclass
class PaperPosition:
    symbol: str
    side: str
    entry_price: float
    quantity: float

    def unrealized_pnl(self, current_price):
        if self.side == "BUY":
            return (
                current_price - self.entry_price
            ) * self.quantity

        if self.side == "SELL":
            return (
                self.entry_price - current_price
            ) * self.quantity

        return 0.0