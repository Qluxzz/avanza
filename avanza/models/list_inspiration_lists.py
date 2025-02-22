from typing import List, Optional, Union
from pydantic import BaseModel


class StockOrderBook(BaseModel):
    """Used when InspirationListItem.instrumentType is STOCK"""

    change: float
    changePercent: float
    updated: str
    """ Example 2011-11-11T11:11:11.504+0200 """
    priceOneYearAgo: Optional[float] = None
    priceThreeMonthsAgo: Optional[float] = None
    currency: str
    """ ISO 4217 """
    lastPrice: float
    flagCode: str
    """ ISO 3166-1 alpha-2 """
    highlightValue: float
    name: str
    id: str


class FundOrderBook(BaseModel):
    """Used when InspirationListItem.instrumentType is FUND"""

    lastUpdated: str
    """ YYYY-MM-DD """
    changeSinceOneDay: float
    changeSinceThreeMonths: float
    changeSinceOneYear: float
    highlightValue: Optional[float] = None
    name: str
    id: str


class HighlightField(BaseModel):
    label: str
    percent: bool


class Statistics(BaseModel):
    positiveCount: int
    neutralCount: int
    negativeCount: int
    positivePercent: float
    neutralPercent: float
    negativePercent: float


class InspirationListItem(BaseModel):
    orderbooks: List[Union[StockOrderBook, FundOrderBook]]
    averageChange: Optional[float] = None
    highlightField: HighlightField
    averageChangeSinceThreeMonths: float
    imageUrl: str
    """ Relative URL """
    information: Optional[str] = None
    name: str
    id: str
    statistics: Statistics
    instrumentType: str
