from dataclasses import dataclass


@dataclass
class PaperTradeRecord:
    symbol: str
    side: str
    entry_price: float
    exit_price: float
    quantity: float
    realized_pnl: float