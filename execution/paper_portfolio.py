from dataclasses import dataclass


@dataclass
class PaperPortfolio:

    initial_balance: float
    balance: float

    @classmethod
    def create(cls, initial_balance=1000.0):

        return cls(
            initial_balance=initial_balance,
            balance=initial_balance
        )

    def apply_realized_pnl(self, realized_pnl):

        if realized_pnl is None:
            return self.balance

        self.balance += realized_pnl

        return self.balance

    def get_balance(self):

        return self.balance

    def get_total_pnl(self):

        return self.balance - self.initial_balance