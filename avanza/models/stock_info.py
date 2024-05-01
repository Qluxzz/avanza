from typing import List
from pydantic import BaseModel

from .quote import Quote
from .historical_closing_prices import HistoricalClosingPrices
from .listing import Listing


class Sector(BaseModel):
    sectorId: str
    sectorName: str


class ShareInfo(BaseModel):
    value: float
    currency: str
    """ ISO 4217 """


class ReportInfo(BaseModel):
    date: str
    """ YYYY-MM-DD """
    reportType: str


class KeyIndicators(BaseModel):
    numberOfOwners: int
    reportDate: str
    """" YYYY-MM-DD """
    volatility: float
    beta: float
    priceEarningsRatio: float
    priceSalesRatio: float
    evEbitRatio: float
    returnOnEquity: float
    returnOnTotalAssets: float
    equityRatio: float
    capitalTurnover: float
    operatingProfitMargin: float
    netMargin: float
    marketCapital: ShareInfo
    equityPerShare: ShareInfo
    turnoverPerShare: ShareInfo
    earningsPerShare: ShareInfo
    dividendsPerYear: int
    nextReport: ReportInfo
    previousReport: ReportInfo


class StockInfo(BaseModel):
    orderbookId: str
    name: str
    isin: str
    instrumentId: str
    sectors: List[Sector]
    tradable: str
    listing: Listing
    historicalClosingPrices: HistoricalClosingPrices
    keyIndicators: KeyIndicators
    quote: Quote
    type: str
