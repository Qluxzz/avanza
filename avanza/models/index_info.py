from typing import Any, List
from pydantic import BaseModel


class Listing(BaseModel):
    shortName: str
    tickerSymbol: str
    countryCode: str
    """ ISO 3166-1 alpha-2 """
    currency: str
    """ ISO 4217 """
    marketPlaceCode: str
    marketPlaceName: str
    tickSizeListId: str
    marketTradesAvailable: bool


class HistoricalClosingPrices(BaseModel):
    oneDay: float
    oneWeek: float
    oneMonth: float
    threeMonths: float
    startOfYear: float
    oneYear: float
    threeYears: float
    fiveYears: float
    tenYears: float
    start: float
    startDate: str
    """ YYYY-MM-DD """


class KeyIndicators(BaseModel):
    numberOfOwners: int
    dividendsPerYear: int


class Quote(BaseModel):
    last: float
    highest: float
    lowest: float
    change: float
    changePercent: float
    timeOfLast: int
    """ Unix timestamp (millisecond) """
    totalValueTraded: float
    totalVolumeTraded: int
    updated: int
    """ Unix timestamp (millisecond) """


class IndexInfo(BaseModel):
    orderbookId: str
    name: str
    isin: str
    instrumentId: str
    sectors: List[Any]
    tradable: str
    listing: Listing
    historicalClosingPrices: HistoricalClosingPrices
    keyIndicators: KeyIndicators
    quote: Quote
    type: str
    """ INDEX """
