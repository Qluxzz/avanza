from typing import List
from pydantic import BaseModel


class TopHit(BaseModel):
    currency: str
    """ ISO 4217 """
    changePercent: float
    lastPrice: float
    name: str
    id: str
    flagCode: str
    """ ISO 3166-1 alpha-2 """
    tradable: bool
    tickerSymbol: str


class Hit(BaseModel):
    instrumentType: str
    numberOfHits: int
    topHits: List[TopHit]


class StockSearchResult(BaseModel):
    totalNumberOfHits: int
    hits: List[Hit]
