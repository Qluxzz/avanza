from typing import List
from pydantic import BaseModel

class InsiderTransaction(BaseModel):
    orderbookId: str | None
    transactionDate: str
    reportedDate: str
    insiderName: str
    transactionType: str
    price: float
    quantity: int
    ownershipChangeFraction: float | None
    insiderPosition: str
    currency: str
    totalValue: float
    marketTransaction: bool
    equityProgram: bool
    ticker: str | None
    marketCountryCode: str | None
    instrumentType: str
    instrumentDescription: str
    owner: str | None


class InsiderTransactions(BaseModel):
    transactions: List[InsiderTransaction]
    buyCount: int
    buyTotalValue: float
    sellCount: int
    sellTotalValue: float
    allocationTotalValue: float