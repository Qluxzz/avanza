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
    buy: QuoteInfo | None = None
    sell: QuoteInfo | None = None
    highest: QuoteInfo | None = None
    lowest: QuoteInfo | None = None
    latest: QuoteInfo | None = None
    change: QuoteInfo | None = None
    changePercent: QuoteInfo | None = None


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


class PositionData(BaseModel):
    account: Account
    instrument: Instrument
    volume: Volume
    value: Value
    averageAcquiredPrice: Value
    averageAcquiredPriceInstrumentCurrency: Value
    acquiredValue: Value
    id: str

class WithOrderbook(PositionData):
    lastTradingDayPerformance: Performance

class WithoutOrderbook(PositionData):
    lastTradingDayPerformance: Optional[Performance]

class CashPosition(BaseModel):
    account: Account
    totalBalance: Value
    id: str


class AccountPositions(BaseModel):
    withOrderbook: List[WithOrderbook]
    withoutOrderbook: List[WithoutOrderbook]
    cashPositions: List[CashPosition]
