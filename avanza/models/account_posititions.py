from typing import Optional, List
from pydantic import BaseModel


class QuoteInfo(BaseModel):
    value: float
    unit: str
    unitType: str
    decimalPrecision: int


class LastDeal(BaseModel):
    date: str
    time: Optional[str]


class Turnover(BaseModel):
    volume: QuoteInfo
    value: Optional[QuoteInfo]


class Quote(BaseModel):
    highest: QuoteInfo
    lowest: QuoteInfo
    latest: QuoteInfo
    change: QuoteInfo
    changePercent: QuoteInfo


class Orderbook(BaseModel):
    id: str
    flagCode: Optional[str]
    """ ISO 3166-1 alpha-2 """
    name: str
    type: str
    tradeStatus: str
    quote: Quote
    turnover: Turnover
    lastDeal: Optional[LastDeal]


class Instrument(BaseModel):
    type: str
    name: str
    orderbook: Optional[Orderbook]
    currency: str
    """ ISO 4217 """
    isin: str
    volumeFactor: float


class Account(BaseModel):
    id: str
    type: str
    name: str
    urlParameterId: str
    hasCredit: bool


class Volume(BaseModel):
    value: float
    unit: str
    unitType: str
    decimalPrecision: int


class Value(BaseModel):
    value: float
    unit: str
    unitType: str
    decimalPrecision: int


class Performance(BaseModel):
    absolute: QuoteInfo
    relative: QuoteInfo


class WithOrderbook(BaseModel):
    account: Account
    instrument: Instrument
    volume: Volume
    value: Value
    averageAcquiredPrice: Value
    acquiredValue: Value
    lastTradingDayPerformance: Performance
    id: str


class WithoutOrderbook(BaseModel):
    account: Account
    instrument: Instrument
    volume: Volume
    value: Value
    averageAcquiredPrice: Value
    acquiredValue: Value
    lastTradingDayPerformance: Optional[Performance]
    id: str


class CashPosition(BaseModel):
    account: Account
    totalBalance: Value
    id: str


class AccountPositions(BaseModel):
    withOrderbook: List[WithOrderbook]
    withoutOrderbook: List[WithoutOrderbook]
    cashPositions: List[CashPosition]
