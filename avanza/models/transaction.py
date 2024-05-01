from typing import List, Optional
from pydantic import BaseModel, Field


class Account(BaseModel):
    id: str
    name: str
    type: str
    urlParameterId: str


class Orderbook(BaseModel):
    id: str
    flagCode: Optional[str]
    """ ISO 3166-1 alpha-2 """
    name: str
    marketplace: str
    type: str
    currency: str
    """ ISO 4217 """
    isin: str
    volumeFactor: float


class Info(BaseModel):
    value: float
    unit: str
    unitType: str
    decimalPrecision: int


class Transaction(BaseModel):
    id: str
    date: str
    """ Example 2011-11-11T11:11:11 """
    settlementDate: str
    """ YYYY-MM-DD """
    availabilityDate: str
    """ YYYY-MM-DD """
    tradeDate: str
    """ YYYY-MM-DD """
    account: Account
    orderbook: Optional[Orderbook]
    instrumentName: Optional[str]
    description: str
    type: str
    volume: Optional[Info]
    priceInTradedCurrency: Optional[Info]
    amount: Info
    onCreditAccount: bool
    comission: Optional[Info]
    currencyRate: Optional[str]
    noteId: Optional[str]
    priceInAccountCurrency: Optional[Info]
    intraday: bool
    foreignTaxRate: Optional[str]
    isin: str
    result: Optional[Info]
    volumeFactor: Optional[float]


class DateRange(BaseModel):
    from_: str = Field(..., alias="from")
    """ YYYY-MM-DD """
    to: str
    """ YYYY-MM-DD """


class TransactionsFilter(BaseModel):
    accountIds: Optional[List[str]]
    transactionTypes: Optional[List[str]]
    isin: Optional[str]
    dateRange: DateRange


class Transactions(BaseModel):
    transactions: List[Transaction]
    transactionsAfterFiltering: int
    transactionsFilter: TransactionsFilter
    firstTransactionDate: str
    """ YYYY-MM-DD """
