from pydantic import BaseModel
from typing import List
from datetime import date

class TickSizeEntry(BaseModel):
    min: float
    max: float
    tick: float

class TickSizeList(BaseModel):
    tickSizeEntries: List[TickSizeEntry]

class FeatureSupport(BaseModel):
    stopLoss: bool
    fillAndOrKill: bool
    openVolume: bool
    marketTrades: bool
    marketTradesSummary: bool
    nordicAtMid: bool
    stopLossMarketMakerQuote: bool
    routingStrategies: bool

class OrderBook(BaseModel):
    id: str
    name: str
    isin: str
    instrumentId: str
    marketPlace: str
    countryCode: str
    tickSizeList: TickSizeList
    collateralValue: float
    currency: str
    """ ISO 4217 """
    orderbookStatus: str
    minValidUntil: str
    """ Example 2025-11-08 """
    maxValidUntil: str
    """ Example 2025-11-08 """
    instrumentType: str
    volumeFactor: float
    featureSupport: FeatureSupport
    priceType: str
    tradingUnit: int
    tickerSymbol: str